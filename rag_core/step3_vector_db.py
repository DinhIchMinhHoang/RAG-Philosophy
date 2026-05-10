"""
step3_vector_db.py - Module Vector Database (Qdrant Persistent + InMemoryStore).

Kiến trúc:
  • child_docs  → được nhúng thành vector và lưu vào Qdrant (persistent trên disk).
  • parent_docs → được lưu vào InMemoryStore (tra cứu theo doc_id → full context).
  • Trả về cả 3 thành phần (docstore, vectorstore, child_docs) để Step 4
    xây dựng HybridMultiVectorRetriever (BM25 + Dense Ensemble).

Public API:
  build_vector_db(child_docs, parent_docs, force_recreate=False)
    -> (InMemoryStore, QdrantVectorStore, List[Document])

Metadata BẢO TỒN:
  Mỗi Document có đầy đủ {'source': str, 'page': int, 'doc_id': str}.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain.retrievers import MultiVectorRetriever

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

    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": "cuda",           # Thay bằng 'cuda' nếu có GPU
            "trust_remote_code": True, # Bắt buộc cho Harrier custom architecture
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )

    # embeddings = build_embeddings_from_common()
    logger.info(
        f"[Step 3] ✅ Embedding model '{Config.EMBEDDING_MODEL_NAME}' đã tải thành công"
    )
    return embeddings


def _build_doc_store(parent_docs: List[Document]) -> InMemoryStore:
    """
    Xây dựng InMemoryStore ánh xạ doc_id → Parent Document.

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


def _collection_exists(client: QdrantClient, name: str) -> bool:
    """Kiểm tra xem collection đã tồn tại trong Qdrant hay chưa."""
    existing = [c.name for c in client.get_collections().collections]
    return name in existing


def _collection_has_points(client: QdrantClient, name: str) -> bool:
    """Kiểm tra xem collection có chứa dữ liệu hay không."""
    info = client.get_collection(name)
    return info.points_count > 0


def build_vector_db(
    child_docs: List[Document],
    parent_docs: List[Document],
    force_recreate: bool = False,
) -> Tuple[InMemoryStore, QdrantVectorStore, List[Document]]:
    """
    Xây dựng Qdrant VectorStore (persistent) + InMemoryStore (parent docs).

    Luồng xử lý:
      1. Kết nối Qdrant persistent tại Config.QDRANT_PATH.
      2. Nếu collection đã tồn tại VÀ force_recreate=False → bỏ qua embedding.
      3. Nếu không → tạo collection mới, nhúng và index child_docs.
      4. Luôn xây dựng InMemoryStore cho parent_docs (in-memory, stateless).
      5. Trả về (docstore, vectorstore, child_docs) cho Step 4 xây dựng
         HybridMultiVectorRetriever.

    Args:
        child_docs  : List[Document] từ step2_chunker.chunk_documents().
                      Mỗi doc có metadata {'source', 'page', 'doc_id'}.
        parent_docs : List[Document] từ step2_chunker.chunk_documents().
                      Mỗi doc có metadata {'source', 'page', 'doc_id'}.
        force_recreate : Nếu True → xóa collection cũ và tạo lại từ đầu.

    Returns:
        Tuple (docstore, vectorstore, child_docs):
          - docstore    : InMemoryStore mapping doc_id → Parent Document.
          - vectorstore : QdrantVectorStore với child_docs đã được index.
          - child_docs  : List[Document] gốc — dùng cho BM25Retriever.

    Raises:
        ValueError: Nếu child_docs hoặc parent_docs rỗng.
        KeyError:   Nếu bất kỳ parent_doc nào thiếu 'doc_id'.
    """
    if not child_docs:
        raise ValueError("child_docs rỗng — không có gì để nhúng vào Qdrant.")
    if not parent_docs:
        raise ValueError("parent_docs rỗng — không có gì để lưu vào InMemoryStore.")

    logger.info(
        f"[Step 3] Bắt đầu xây dựng vector DB: "
        f"{len(child_docs)} child docs, {len(parent_docs)} parent docs"
    )

    # 1. Embedding model (luôn cần — cho cả index lẫn query)
    embeddings = _init_embeddings()

    # 2. Kết nối Qdrant persistent
    client = QdrantClient(path=Config.QDRANT_PATH)
    exists = _collection_exists(client, Config.QDRANT_COLLECTION)
    has_data = exists and _collection_has_points(client, Config.QDRANT_COLLECTION)
#====================================================hehehehehehe==============================
    # ── Dimension Validation & Auto-Invalidation ─────────────────────
    if exists:
        try:
            collection_info = client.get_collection(Config.QDRANT_COLLECTION)
            
            # Extract dimension gracefully handling structural differences
            old_dim = None
            vectors_config = getattr(collection_info.config.params, 'vectors', None)
            
            if vectors_config:
                if hasattr(vectors_config, 'size'):
                    old_dim = vectors_config.size
                elif isinstance(vectors_config, dict) and len(vectors_config) > 0:
                    first_vector = next(iter(vectors_config.values()))
                    old_dim = getattr(first_vector, 'size', None)
                    
            if old_dim is not None and old_dim != Config.EMBEDDING_DIM:
                logger.warning(
                    f"⚠️ Dimension mismatch detected (Storage: {old_dim}, Config: {Config.EMBEDDING_DIM}). "
                    f"Forcing index recreation."
                )
                print(
                    f"\n⚠️  Dimension mismatch detected (Storage: {old_dim}, Config: {Config.EMBEDDING_DIM}). "
                    f"Forcing index recreation..."
                )
                force_recreate = True
        except Exception as e:
            logger.warning(f"[Step 3] ⚠️ Không thể kiểm tra collection dimension: {e}")
#====================================================================ehheheheheh========================================
    if has_data and not force_recreate:
        # ── Collection đã có dữ liệu → bỏ qua embedding, chỉ kết nối ──
        logger.info(
            f"[Step 3] Collection '{Config.QDRANT_COLLECTION}' đã tồn tại với dữ liệu. "
            f"Bỏ qua re-indexing (force_recreate=False)."
        )
        vectorstore = QdrantVectorStore(
            client=client,
            collection_name=Config.QDRANT_COLLECTION,
            embedding=embeddings,
        )
    else:
        # ── Tạo mới hoặc tạo lại collection ──────────────────────────
        if exists:
            logger.info(
                f"[Step 3] Xóa collection cũ '{Config.QDRANT_COLLECTION}' "
                f"(force_recreate={force_recreate}, has_data={has_data})"
            )
            client.delete_collection(Config.QDRANT_COLLECTION)

        # Tạo collection với đúng vector dimension
        logger.info(
            f"[Step 3] Tạo collection '{Config.QDRANT_COLLECTION}' "
            f"(dim={Config.EMBEDDING_DIM}, distance=Cosine)"
        )
        client.create_collection(
            collection_name=Config.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=Config.EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )

        # Tạo VectorStore instance và index documents
        vectorstore = QdrantVectorStore(
            client=client,
            collection_name=Config.QDRANT_COLLECTION,
            embedding=embeddings,
        )

        logger.info(
            f"[Step 3] Đang nhúng {len(child_docs)} child docs vào Qdrant..."
        )
        vectorstore.add_documents(child_docs)
        logger.info(
            f"[Step 3] ✅ Đã index {len(child_docs)} child docs vào Qdrant"
        )

    # 3. InMemoryStore cho parent_docs (luôn build mới — stateless)
    docstore = _build_doc_store(parent_docs)

    logger.info(
        f"[Step 3] ✅ Qdrant persistent store sẵn sàng "
        f"(path='{Config.QDRANT_PATH}', collection='{Config.QDRANT_COLLECTION}')"
    )

    return docstore, vectorstore, child_docs


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

    # Step 3: Build vector DB (force_recreate=True cho test)
    docstore, vectorstore, child_docs_out = build_vector_db(
        child_docs, parent_docs, force_recreate=True
    )

    # Test query qua vectorstore
    query = "Triết học là gì?"
    print(f"\n🔍 Dense search: \"{query}\"")
    results = vectorstore.similarity_search(query, k=3)

    print(f"\n{'─'*55}")
    print(f"📊 KẾT QUẢ ({len(results)} child docs):")
    for i, doc in enumerate(results):
        source = doc.metadata.get("source", "N/A")
        page   = doc.metadata.get("page",   "N/A")
        doc_id = doc.metadata.get("doc_id", "N/A")
        print(f"\n  [{i+1}] source={os.path.basename(source)}, page={page}, "
              f"doc_id={doc_id[:8]}...")
        print(f"       nội dung (300 ký tự): {doc.page_content[:300]!r}")
    print(f"{'─'*55}")
    print(f"\n✅ Step 3 test hoàn tất!")
    print(f"   docstore: {type(docstore).__name__}")
    print(f"   vectorstore: {type(vectorstore).__name__}")
    print(f"   child_docs: {len(child_docs_out)} docs")
"""
step3_vector_db.py
"""
