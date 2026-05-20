from __future__ import annotations

<<<<<<< HEAD
Kiến trúc Parent-Document Retrieval:
  • child_docs  → được nhúng thành vector và lưu vào Qdrant (vector search).
  • parent_docs → được lưu vào InMemoryStore (tra cứu theo doc_id → full context).
  • MultiVectorRetriever kết nối hai kho trên qua id_key="doc_id":
      1. Tìm child_docs gần nhất trong Qdrant.
      2. Dùng doc_id của child để lấy parent tương ứng từ InMemoryStore.
      3. Trả Parent Documents cho LLM → câu trả lời có ngữ cảnh đầy đủ.

Public API:
  build_vector_db(child_docs, parent_docs) -> MultiVectorRetriever

Metadata BẢO TỒN:
  Mỗi Document trả về bởi retriever có đầy đủ {'source': str, 'page': int}.
"""

from __future__ import annotations

import logging
=======
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
from typing import List

from langchain.retrievers import MultiVectorRetriever
from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

<<<<<<< HEAD
from common.logging_utils import configure_logging, get_logger
from common.embeddings import build_embeddings as build_embeddings_from_common
from config import Config

configure_logging()
logger = get_logger(__name__)


def _init_embeddings() -> HuggingFaceEmbeddings:
    """
    Khởi tạo HuggingFaceEmbeddings cho Harrier model.

    Cấu hình:
      - model_name: Config.EMBEDDING_MODEL_NAME (microsoft/harrier-oss-v1-270m)
      - device: Config.DEVICE (chuyển sang 'cuda' nếu có GPU)
      - trust_remote_code: True — bắt buộc cho Harrier custom architecture
      - normalize_embeddings: True — chuẩn hóa L2 cho Cosine Similarity chính xác

    Returns:
        HuggingFaceEmbeddings đã sẵn sàng dùng.
    """
    logger.info(
        f"[Step 3] Đang tải embedding model: {Config.EMBEDDING_MODEL_NAME}"
    )
    embeddings = build_embeddings_from_common()
    logger.info(
        f"[Step 3] ✅ Embedding model '{Config.EMBEDDING_MODEL_NAME}' đã tải thành công"
    )
    return embeddings
=======
try:
    from .common.embeddings import build_embeddings as build_embeddings_from_common
    from .config import Config
    from .hybrid_retriever import BM25ChildIndex, HybridParentRetriever
    from .rerank_retriever import ChildRerankParentRetriever
except ImportError:  # pragma: no cover
    from common.embeddings import build_embeddings as build_embeddings_from_common
    from config import Config
    from hybrid_retriever import BM25ChildIndex, HybridParentRetriever
    from rerank_retriever import ChildRerankParentRetriever


def _init_embeddings() -> HuggingFaceEmbeddings:
    return build_embeddings_from_common()
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca


def _build_qdrant_store(
    child_docs: List[Document],
    embeddings: HuggingFaceEmbeddings,
    ids: List[str],
) -> QdrantVectorStore:
    return QdrantVectorStore.from_documents(
        documents=child_docs,
        embedding=embeddings,
        location=Config.QDRANT_LOCATION,
        collection_name=Config.QDRANT_COLLECTION,
        ids=ids,
    )


def _validate_child_docs(child_docs: List[Document]) -> None:
    for idx, doc in enumerate(child_docs):
        if not doc.metadata.get("doc_id"):
            raise KeyError(f"child_docs[{idx}] missing doc_id in metadata")


def _build_doc_store(parent_docs: List[Document]) -> InMemoryStore:
    store = InMemoryStore()
    for idx, doc in enumerate(parent_docs):
        if "doc_id" not in doc.metadata:
            raise KeyError(f"parent_docs[{idx}] missing doc_id in metadata")
    store.mset([(doc.metadata["doc_id"], doc) for doc in parent_docs])
    return store


def build_vector_db(child_docs: List[Document], parent_docs: List[Document]):
    if not child_docs:
        raise ValueError("child_docs is empty")
    if not parent_docs:
        raise ValueError("parent_docs is empty")

    _validate_child_docs(child_docs)

    # Bóc tách ID vật lý (Lập trình phòng thủ — Fail-fast)
    child_ids: List[str] = []
    for idx, doc in enumerate(child_docs):
        point_id = doc.metadata.pop("_child_point_id", None)
        if point_id is None:
            raise ValueError(
                f"child_docs[{idx}] missing '_child_point_id' in metadata. "
                "Ensure step 2 ran correctly."
            )
        child_ids.append(point_id)

    embeddings = _init_embeddings()
    vectorstore = _build_qdrant_store(child_docs, embeddings, ids=child_ids)
    doc_store = _build_doc_store(parent_docs)

    # Rerank mode: always use dense+BM25 to get child candidates, rerank children,
    # then map to parent docs (fail-open if Cohere not available).
    if Config.RERANK_ENABLED:
        bm25_index = BM25ChildIndex.from_documents(child_docs)
        final_parent_k = Config.HYBRID_FINAL_K if Config.HYBRID_ENABLED else Config.TOP_K_RESULTS
        return ChildRerankParentRetriever(
            vectorstore=vectorstore,
            docstore=doc_store,
            bm25_index=bm25_index,
            id_key="doc_id",
            final_parent_k=final_parent_k,
        )

    if Config.HYBRID_ENABLED:
        return HybridParentRetriever(
            vectorstore=vectorstore,
            docstore=doc_store,
            bm25_index=BM25ChildIndex.from_documents(child_docs),
            id_key="doc_id",
        )

    return MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=doc_store,
        id_key="doc_id",
        search_kwargs={"k": Config.TOP_K_RESULTS},
    )
