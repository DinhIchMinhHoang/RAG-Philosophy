"""
step4_generator.py - Hybrid Retrieval (BM25 + Dense Ensemble + Cohere Rerank) & Generation.

Kiến trúc 3-Stage Hybrid Retrieval:
  Stage 1 — EnsembleRetriever (Weighted RRF):
    • Dense Retriever : Qdrant similarity search trên child_docs.
    • BM25 Retriever  : In-memory BM25 trên child_docs (ViTokenizer preprocessor).
    → Trả về Top-K fused CHILD Docs (cùng entity type → RRF hợp lệ).

  Stage 2 — ContextualCompressionRetriever (Cohere Rerank):
    • Nhận Top-K fused child docs từ Stage 1.
    • CohereRerank re-score → trả về Top-N reranked child docs.
    → Metadata (doc_id) được bảo toàn nguyên vẹn.

  Stage 3 — HybridMultiVectorRetriever (Parent-Child Lookup):
    • Nhận reranked child docs từ Stage 2.
    • Map doc_id metadata → InMemoryStore → trả về PARENT Docs.
    → LLM nhận Parent Docs (ngữ cảnh đầy đủ) để trả lời.

Public API:
  setup_rag_chain(docstore, vectorstore, child_docs) -> RAG chain
  ask(rag_chain, question) -> dict with 'answer' and 'sources'
"""

from __future__ import annotations

import logging
import os
from typing import List

from langchain_community.retrievers import BM25Retriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.stores import InMemoryStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_qdrant import QdrantVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from config import Config

configure_logging()
logger = get_logger(__name__)


# ── Vietnamese BM25 Preprocessing ─────────────────────────────────────────────

def vi_tokenize_for_bm25(text: str) -> list[str]:
    """
    Tiền xử lý văn bản tiếng Việt cho BM25.

    ViTokenizer.tokenize() ghép từ ghép bằng dấu '_' (VD: "triết_học").
    Sau đó .lower().split() chuyển thành danh sách token lowercase.

    Args:
        text: Văn bản tiếng Việt gốc.

    Returns:
        List[str] — danh sách token đã segment.
    """
    from pyvi import ViTokenizer
    return ViTokenizer.tokenize(text).lower().split()


# ── HybridMultiVectorRetriever ────────────────────────────────────────────────

class HybridMultiVectorRetriever(BaseRetriever):
    """
    Custom retriever kết hợp Reranked Retriever (Ensemble + Cohere Rerank)
    với Parent-Child doc_id lookup.

    Luồng:
      1. base_retriever.invoke(query) → Top-K reranked child docs.
      2. Extract doc_id từ mỗi child doc metadata.
      3. docstore.mget([doc_ids]) → Parent Docs tương ứng.
      4. Trả về Parent Docs (full context) cho LLM.

    Metadata (source, page, doc_id) được bảo toàn nguyên vẹn trên Parent Docs
    vì chúng được lấy trực tiếp từ InMemoryStore — không qua bất kỳ transform nào.
    """
    base_retriever: BaseRetriever
    docstore: InMemoryStore
    id_key: str = "doc_id"

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """
        Lấy Parent Documents thông qua 3-stage hybrid retrieval.

        Stage 1: EnsembleRetriever (RRF trên child docs).
        Stage 2: CohereRerank (re-score + filter).
        Stage 3: doc_id → Parent lookup từ InMemoryStore.
        """
        # Stage 1+2: Ensemble + Rerank → reranked child docs
        fused_children = self.base_retriever.invoke(query)

        if not fused_children:
            logger.warning("[Step 4] Reranked Retriever trả về 0 kết quả.")
            return []

        logger.info(
            f"[Step 4] Reranked Retriever → {len(fused_children)} reranked child docs"
        )

        # Stage 3: Map doc_id → Parent Docs
        doc_ids: list[str] = []
        for child in fused_children:
            doc_id = child.metadata.get(self.id_key)
            if doc_id:
                doc_ids.append(doc_id)
            else:
                logger.warning(
                    f"[Step 4] Child doc thiếu '{self.id_key}' trong metadata. "
                    f"Bỏ qua. Metadata: {child.metadata}"
                )

        if not doc_ids:
            logger.warning("[Step 4] Không có doc_id hợp lệ để tra cứu Parent.")
            return fused_children  # Fallback: trả child docs nếu parent lookup thất bại

        # Deduplicate doc_ids (nhiều child có thể cùng 1 parent)
        unique_doc_ids = list(dict.fromkeys(doc_ids))

        # Fetch parent docs từ InMemoryStore
        parent_docs_raw = self.docstore.mget(unique_doc_ids)

        parent_docs: list[Document] = []
        for doc_id, parent in zip(unique_doc_ids, parent_docs_raw):
            if parent is not None:
                parent_docs.append(parent)
            else:
                logger.warning(
                    f"[Step 4] doc_id='{doc_id[:8]}...' "
                    f"không tìm thấy trong InMemoryStore."
                )

        logger.info(
            f"[Step 4] Parent lookup: {len(unique_doc_ids)} unique doc_ids "
            f"→ {len(parent_docs)} parent docs"
        )

        return parent_docs


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Bạn là chuyên gia AI, trợ lý học tập cho sinh viên "
    "Đại học Công nghệ (UET). Bạn sẽ nhận được các đoạn trích dẫn "
    "từ giáo trình. Hãy trả lời câu hỏi dựa TRỰC TIẾP trên "
    "các đoạn văn được cung cấp dưới đây.\n\n"
    "Quy tắc:\n"
    "1. Chỉ sử dụng thông tin từ tài liệu được cung cấp.\n"
    "2. Nếu thông tin không đủ, hãy chỉ ra phần nào thiếu "
    "thay vì tự ý bổ sung.\n"
    # "3. Luôn đính kèm số trang (VD: [Trang X]) vào cuối "
    # "mỗi ý quan trọng trong câu trả lời.\n\n"
    "Tài liệu tham khảo:\n"
    "{context}"
)


# ── RAG Chain Setup ───────────────────────────────────────────────────────────

def setup_rag_chain(
    docstore: InMemoryStore,
    vectorstore: QdrantVectorStore,
    child_docs: List[Document],
):
    """
    Thiết lập RAG chain với Hybrid Retrieval (BM25 + Dense Ensemble).

    Luồng xử lý:
      1. Dense Retriever: vectorstore.as_retriever() → top-K child docs.
      2. BM25 Retriever: BM25Retriever.from_documents() → top-K child docs.
      3. EnsembleRetriever: RRF merge Dense + BM25 → fused child docs.
      4. HybridMultiVectorRetriever: fused child → doc_id → Parent docs.
      5. RAG Chain: Parent docs → Prompt → LLM → Answer + Citations.

    Args:
        docstore    : InMemoryStore từ step3 (doc_id → Parent Doc).
        vectorstore : QdrantVectorStore từ step3 (child docs đã index).
        child_docs  : List[Document] gốc từ step3 (dùng cho BM25Retriever).

    Returns:
        RAG chain sẵn sàng nhận câu hỏi qua method invoke().
    """
    logger.info(f"[Step 4] Đang khởi tạo Hybrid RAG chain...")

    # ── Dense Retriever (Qdrant) ──────────────────────────────────────
    dense_retriever = vectorstore.as_retriever(
        search_kwargs={"k": Config.TOP_K_RESULTS}
    )
    logger.info(
        f"[Step 4] Dense retriever: Qdrant top_k={Config.TOP_K_RESULTS}"
    )

    # ── BM25 Retriever (In-Memory, ViTokenizer) ──────────────────────
    bm25_retriever = BM25Retriever.from_documents(
        child_docs,
        preprocess_func=vi_tokenize_for_bm25,
    )
    bm25_retriever.k = Config.TOP_K_RESULTS
    logger.info(
        f"[Step 4] BM25 retriever: {len(child_docs)} child docs, "
        f"top_k={Config.TOP_K_RESULTS}, preprocessor=ViTokenizer"
    )

    # ── Retrieve Feature Flags ────────────────────────────────────────
    from config import FeatureFlags
    
    # ── Ensemble Retriever (Weighted RRF) ─────────────────────────────
    dense_weight = Config.HYBRID_ALPHA
    bm25_weight = 1.0 - Config.HYBRID_ALPHA

    ensemble_retriever = EnsembleRetriever(
        retrievers=[dense_retriever, bm25_retriever],
        weights=[dense_weight, bm25_weight],
    )
    logger.info(
        f"[Step 4] EnsembleRetriever: "
        f"weights=[Dense={dense_weight}, BM25={bm25_weight}]"
    )

    if FeatureFlags.USE_RERANKER:
        if Config.COHERE_API_KEY:
            # ── Priority 1: Cohere Reranker ──────────────────────────────────
            from langchain_cohere import CohereRerank
            compressor = CohereRerank(
                cohere_api_key=Config.COHERE_API_KEY,
                model=Config.COHERE_RERANK_MODEL,
                top_n=Config.TOP_K_RERANK,
            )
            logger.info(
                f"[Step 4] CohereRerank initialized: model={Config.COHERE_RERANK_MODEL}, "
                f"top_n={Config.TOP_K_RERANK}"
            )
        else:
            # ── Priority 2: Flashrank Reranker (Fallback) ────────────────────
            from langchain.retrievers.document_compressors import FlashrankRerank
            compressor = FlashrankRerank(top_n=Config.TOP_K_RERANK)
            logger.info(
                f"[Step 4] FlashrankRerank initialized as fallback with top_n={Config.TOP_K_RERANK}"
            )
        
        final_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=ensemble_retriever,
        )
    else:
        logger.info("[Step 4] Reranker is disabled via FeatureFlags. Using EnsembleRetriever directly.")
        final_retriever = ensemble_retriever

    # ── Hybrid Multi-Vector Retriever (Child → Parent Lookup) ─────────
    hybrid_retriever = HybridMultiVectorRetriever(
        base_retriever=final_retriever,
        docstore=docstore,
        id_key="doc_id",
    )
    logger.info("[Step 4] ✅ HybridMultiVectorRetriever sẵn sàng")

    # ── LLM (Gemini) ──────────────────────────────────────────────────
    logger.info(f"[Step 4] Đang khởi tạo LLM: {Config.LLM_MODEL}")
    
    if not Config.GEMINI_API_KEY:
        raise ValueError("CRITICAL ERROR: 'GEMINI_API_KEY' is missing or empty in Config.")
    os.environ["GOOGLE_API_KEY"] = Config.GEMINI_API_KEY

    llm = ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        temperature=0.2,
        api_key=Config.GEMINI_API_KEY,
    )

    # ── Prompt Template ───────────────────────────────────────────────
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    # ── RAG Chain ─────────────────────────────────────────────────────
    question_answer_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt,
    )

    rag_chain = create_retrieval_chain(
        retriever=hybrid_retriever,
        combine_docs_chain=question_answer_chain,
    )

    logger.info("✅ Hybrid RAG chain (BM25 + Dense Ensemble) sẵn sàng")
    return rag_chain


def ask(rag_chain, question: str) -> dict:
    """
    Gửi câu hỏi tới RAG chain và trả về kết quả.

    Args:
        rag_chain: RAG chain từ setup_rag_chain().
        question: Câu hỏi của người dùng.

    Returns:
        Dict chứa 'answer' (câu trả lời) và 'sources' (tài liệu tham khảo).
    """
    logger.info(f"Câu hỏi: \"{question}\"")

    result = rag_chain.invoke({"input": question})

    # Trích xuất thông tin citations từ context
    sources = []
    for doc in result.get("context", []):
        page = doc.metadata.get("page", "N/A")
        source = doc.metadata.get("source", "N/A")
        sources.append({"page": page, "source": source})

    return {
        "answer": result.get("answer", ""),
        "sources": sources,
    }
