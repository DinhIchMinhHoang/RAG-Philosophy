"""
step3_vector_db.py - Module nhúng (Embedding) và lưu vào Qdrant.

Sử dụng HuggingFaceEmbeddings để nhúng văn bản thành vector,
sau đó lưu vào Qdrant VectorStore để phục vụ truy xuất.
"""

import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from config import Config

logger = logging.getLogger(__name__)


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Khởi tạo và trả về đối tượng HuggingFaceEmbeddings.

    Sử dụng model tiếng Việt từ Config.EMBEDDING_MODEL.
    Vector được normalize để tính Cosine Similarity chính xác.

    Returns:
        Đối tượng HuggingFaceEmbeddings đã cấu hình.
    """
    logger.info(f"Đang khởi tạo Local Embedding Model: {Config.EMBEDDING_MODEL}")

    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    logger.info("✅ Khởi tạo Embedding Model thành công")
    return embeddings


def ingest_into_qdrant(chunks: list[Document]) -> QdrantVectorStore:
    """
    Nhúng danh sách Document chunks thành vector và lưu vào Qdrant.

    Args:
        chunks: Danh sách Document đã được chia nhỏ từ step2_chunker.

    Returns:
        Đối tượng QdrantVectorStore đã chứa dữ liệu.
    """
    logger.info(f"Đang nhúng {len(chunks)} chunks vào Qdrant...")

    # Khởi tạo embedding model
    embeddings = get_embeddings()

    # Tạo VectorStore từ documents
    vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        path=Config.QDRANT_PATH,
        collection_name=Config.QDRANT_COLLECTION,
    )

    logger.info(
        f"✅ Đã nhúng và lưu {len(chunks)} chunks vào Qdrant "
        f"(collection: '{Config.QDRANT_COLLECTION}')"
    )
    return vectorstore


def get_retriever(vectorstore: QdrantVectorStore):
    """
    Tạo retriever từ vectorstore để truy xuất tài liệu.

    Args:
        vectorstore: Đối tượng QdrantVectorStore đã khởi tạo.

    Returns:
        Retriever object với top-k kết quả từ Config.
    """
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": Config.TOP_K_RESULTS}
    )

    logger.info(f"✅ Retriever đã sẵn sàng (top_k={Config.TOP_K_RESULTS})")
    return retriever


# ── Test block ────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    from step1_loader import load_pdf
    from step2_chunker import split_documents

    try:
        # 1. Load PDF
        pdf_path = os.path.join(Config.DATA_DIR, "Triết_Mác_Lenin.pdf")
        docs = load_pdf(pdf_path)

        # 2. Chunking
        chunks = split_documents(docs)

        # 3. Nhúng và lưu vào Qdrant
        vectorstore = ingest_into_qdrant(chunks)

        # 4. Tạo retriever và thử truy vấn
        retriever = get_retriever(vectorstore)

        query = "mạng nơ ron là gì?"
        print(f"\n{'='*50}")
        print(f"Truy vấn: \"{query}\"")
        print(f"{'='*50}")

        results = retriever.invoke(query)

        for i, doc in enumerate(results):
            print(f"\n--- Kết quả #{i+1} ---")
            print(f"Trang : {doc.metadata.get('page', 'N/A')}")
            print(f"Nguồn : {doc.metadata.get('source', 'N/A')}")
            print(f"Nội dung (300 ký tự):")
            print(doc.page_content)

    except Exception as e:
        logger.error(f"❌ Lỗi khi chạy test: {e}")
        raise
