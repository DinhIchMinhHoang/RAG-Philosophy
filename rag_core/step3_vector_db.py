"""
step3_vector_db.py - Module Vector Database (Qdrant + MultiVectorRetriever).

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

import logging
from typing import List

from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
try:
    # LangChain may expose MultiVectorRetriever at different locations depending on version
    from langchain.retrievers.multi_vector import MultiVectorRetriever
except Exception:
    try:
        from langchain.retrievers import MultiVectorRetriever
    except Exception:
        # Provide clear ImportError when unavailable
        raise ImportError(
            "MultiVectorRetriever not found in langchain. Install a compatible langchain version."
        )


from config import Config

# ── Logger ────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


def _init_embeddings() -> HuggingFaceEmbeddings:
    """
    Khởi tạo HuggingFaceEmbeddings cho Harrier model.

    Cấu hình:
      - model_name: Config.EMBEDDING_MODEL_NAME (microsoft/harrier-oss-v1-270m)
      - device: cpu (chuyển sang 'cuda' nếu có GPU)
      - trust_remote_code: True — bắt buộc cho Harrier custom architecture
      - normalize_embeddings: True — chuẩn hóa L2 cho Cosine Similarity chính xác

    Returns:
        HuggingFaceEmbeddings đã sẵn sàng dùng.
    """
    logger.info(
        f"[Step 3] Đang tải embedding model: {Config.EMBEDDING_MODEL_NAME}"
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": "cpu",           # Thay bằng 'cuda' nếu có GPU
            "trust_remote_code": True, # Bắt buộc cho Harrier custom architecture
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )

    logger.info(
        f"[Step 3] ✅ Embedding model '{Config.EMBEDDING_MODEL_NAME}' đã tải thành công"
    )
    return embeddings


def _build_qdrant_store(
    child_docs: List[Document],
    embeddings: HuggingFaceEmbeddings,
) -> QdrantVectorStore:
    """
    Tạo Qdrant in-memory collection từ child_docs.

    Child Documents được nhúng và index vào Qdrant để phục vụ
    vector similarity search. Mỗi child giữ doc_id trong metadata
    để MultiVectorRetriever tra cứu Parent tương ứng.

    Args:
        child_docs: Danh sách Child Documents từ Step 2.
        embeddings: HuggingFaceEmbeddings đã khởi tạo.

    Returns:
        QdrantVectorStore đã index child_docs.
    """
    logger.info(
        f"[Step 3] Đang nhúng {len(child_docs)} child docs vào Qdrant "
        f"(collection='{Config.QDRANT_COLLECTION}', location=':memory:')..."
    )

    vectorstore = QdrantVectorStore.from_documents(
        documents=child_docs,
        embedding=embeddings,
        location=":memory:",
        collection_name=Config.QDRANT_COLLECTION,
    )

    logger.info(
        f"[Step 3] ✅ Đã index {len(child_docs)} child docs vào Qdrant"
    )
    return vectorstore


def _build_doc_store(parent_docs: List[Document]) -> InMemoryStore:
    """
    Xây dựng InMemoryStore ánh xạ doc_id → Parent Document.

    MultiVectorRetriever sẽ dùng store này để lấy Parent Document
    đầy đủ sau khi tìm được child match trong Qdrant.

    Args:
        parent_docs: Danh sách Parent Documents từ Step 2.

    Returns:
        InMemoryStore với mapping {doc_id: Document}.

    Raises:
        KeyError: Nếu bất kỳ parent_doc nào thiếu 'doc_id' trong metadata.
    """
    store = InMemoryStore()

    # Kiểm tra toàn bộ parent_docs trước khi insert
    for idx, doc in enumerate(parent_docs):
        if "doc_id" not in doc.metadata:
            raise KeyError(
                f"parent_docs[{idx}] thiếu 'doc_id' trong metadata. "
                f"Metadata hiện tại: {doc.metadata}"
            )

    # Batch insert: [(doc_id, Document), ...]
    store.mset(
        [(doc.metadata["doc_id"], doc) for doc in parent_docs]
    )

    logger.info(
        f"[Step 3] ✅ Đã lưu {len(parent_docs)} parent docs vào InMemoryStore"
    )
    return store


def build_vector_db(
    child_docs: List[Document],
    parent_docs: List[Document],
) -> MultiVectorRetriever:
    """
    Xây dựng và trả về MultiVectorRetriever liên kết Qdrant + InMemoryStore.

    Luồng xử lý:
      1. Tải HuggingFaceEmbeddings (Harrier model).
      2. Index child_docs vào Qdrant (:memory:) — phục vụ vector search.
      3. Lưu parent_docs vào InMemoryStore theo doc_id — phục vụ lookup.
      4. Khởi tạo MultiVectorRetriever kết nối cả hai.

    Khi Step 4 gọi retriever.invoke(query):
      → Qdrant tìm top-k child_docs gần nhất với query.
      → Lấy doc_id từ metadata của mỗi child.
      → InMemoryStore trả về Parent Documents tương ứng.
      → LLM nhận Parent (ngữ cảnh đầy đủ) để trả lời.

    Args:
        child_docs  : List[Document] từ step2_chunker.chunk_documents().
                      Mỗi doc phải có metadata {'source', 'page', 'doc_id'}.
        parent_docs : List[Document] từ step2_chunker.chunk_documents().
                      Mỗi doc phải có metadata {'source', 'page', 'doc_id'}.

    Returns:
        MultiVectorRetriever sẵn sàng dùng cho Step 4.

    Raises:
        ValueError: Nếu child_docs hoặc parent_docs rỗng.
        KeyError:   Nếu bất kỳ document nào thiếu 'doc_id'.
    """
    if not child_docs:
        raise ValueError("child_docs rỗng — không có gì để nhúng vào Qdrant.")
    if not parent_docs:
        raise ValueError("parent_docs rỗng — không có gì để lưu vào InMemoryStore.")

    logger.info(
        f"[Step 3] Bắt đầu xây dựng vector DB: "
        f"{len(child_docs)} child docs, {len(parent_docs)} parent docs"
    )

    # 1. Embedding model
    embeddings = _init_embeddings()

    # 2. Qdrant vectorstore (child_docs)
    vectorstore = _build_qdrant_store(child_docs, embeddings)

    # 3. InMemoryStore (parent_docs, indexed by doc_id)
    doc_store = _build_doc_store(parent_docs)

    # 4. MultiVectorRetriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=doc_store,
        id_key="doc_id",
        search_kwargs={"k": Config.TOP_K_RESULTS},
    )

    logger.info(
        f"[Step 3] ✅ MultiVectorRetriever sẵn sàng "
        f"(top_k={Config.TOP_K_RESULTS}, id_key='doc_id')"
    )
    return retriever


# ── Self-test block ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import os
    import logging as _logging

    _logging.basicConfig(
        level=_logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    sys.path.insert(0, os.path.dirname(__file__))

    from step1_parser import HybridPDFParser
    from step2_chunker import chunk_documents

    pdf_files = [
        f for f in os.listdir(Config.RAW_DIR)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print(f"⚠️  Không tìm thấy PDF nào trong {Config.RAW_DIR}")
        sys.exit(0)

    pdf_path = os.path.join(Config.RAW_DIR, pdf_files[0])
    print(f"\n📄 Đang parse: {pdf_files[0]}")

    # Step 1: Parse → List[Document]
    parser = HybridPDFParser()
    pages = parser.parse_pdf(pdf_path)
    print(f"   → {len(pages)} trang")

    # Step 2: Chunk → child_docs, parent_docs
    child_docs, parent_docs = chunk_documents(pages)

    # Step 3: Build retriever
    retriever = build_vector_db(child_docs, parent_docs)

    # Test query
    query = "Triết học là gì?"
    print(f"\n🔍 Truy vấn: \"{query}\"")
    results = retriever.invoke(query)

    print(f"\n{'─'*55}")
    print(f"📊 KẾT QUẢ ({len(results)} tài liệu trả về — PARENT level):")
    for i, doc in enumerate(results):
        source = doc.metadata.get("source", "N/A")
        page   = doc.metadata.get("page",   "N/A")
        doc_id = doc.metadata.get("doc_id", "N/A")
        print(f"\n  [{i+1}] source={os.path.basename(source)}, page={page}, "
              f"doc_id={doc_id[:8]}...")
        print(f"       nội dung (300 ký tự): {doc.page_content[:300]!r}")
    print(f"{'─'*55}")
    print("\n✅ Step 3 test hoàn tất!")
