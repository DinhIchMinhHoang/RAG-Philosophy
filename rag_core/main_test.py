"""
main_test.py - Kịch bản chạy thử toàn bộ RAG pipeline.

Full flow: Load PDF → Chunking → Embedding + Qdrant → RAG Chain → Chat loop.
"""

import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def build_pipeline(pdf_filename: str = "Triết_Mác_Lenin.pdf"):
    """
    Xây dựng toàn bộ pipeline RAG từ đầu đến cuối.

    Args:
        pdf_filename: Tên file PDF trong thư mục data/.

    Returns:
        rag_chain: RAG chain sẵn sàng nhận câu hỏi.
    """
    from config import Config
    from step1_loader import load_pdf
    from step2_chunker import split_documents
    from step3_vector_db import ingest_into_qdrant, get_retriever
    from step4_generator import setup_rag_chain

    # ── Step 1: Load PDF ──────────────────────────────────────
    pdf_path = os.path.join(Config.DATA_DIR, pdf_filename)
    docs = load_pdf(pdf_path)

    # ── Step 2: Chunking ──────────────────────────────────────
    chunks = split_documents(docs)

    # ── Step 3: Embedding + Qdrant ────────────────────────────
    vectorstore = ingest_into_qdrant(chunks)
    retriever = get_retriever(vectorstore)

    # ── Step 4: RAG Chain ─────────────────────────────────────
    rag_chain = setup_rag_chain(retriever)

    return rag_chain


def chat_loop(rag_chain):
    """
    Vòng lặp chat tương tác — hỏi nhiều câu liên tiếp.
    Gõ 'exit', 'quit' hoặc 'q' để thoát.
    """
    from step4_generator import ask

    print("\n" + "=" * 60)
    print("  RAG PHILOSOPHY — Trợ lý học tập UET")
    print("  Gõ câu hỏi để bắt đầu. Gõ 'q' để thoát.")
    print("=" * 60)

    while True:
        try:
            question = input("\n🧑 Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Tạm biệt!")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            print("👋 Tạm biệt!")
            break

        try:
            result = ask(rag_chain, question)

            # In câu trả lời
            print(f"\n🤖 Trợ lý:\n{result['answer']}")

            # In nguồn trích dẫn
            if result["sources"]:
                print(f"\n📚 Nguồn tham khảo:")
                seen = set()
                for src in result["sources"]:
                    key = (src["page"], src["source"])
                    if key not in seen:
                        seen.add(key)
                        filename = os.path.basename(src["source"])
                        print(f"   - {filename}, Trang {src['page'] + 1}")

        except Exception as e:
            logger.error(f"❌ Lỗi khi xử lý câu hỏi: {e}")
            print(f"⚠️ Đã xảy ra lỗi: {e}")


def main():
    """Entry point chính."""
    print("\n🚀 Đang khởi tạo RAG Pipeline...")
    print("   (Lần đầu có thể mất vài phút để tải model)\n")

    try:
        rag_chain = build_pipeline("Triết_Mác_Lenin.pdf")
        chat_loop(rag_chain)

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        print(f"\n⚠️ Không tìm thấy file PDF. Kiểm tra thư mục data/.")
    except EnvironmentError as e:
        logger.error(f"❌ {e}")
        print(f"\n⚠️ Lỗi cấu hình: {e}")
    except Exception as e:
        logger.error(f"❌ Lỗi không mong muốn: {e}")
        raise


if __name__ == "__main__":
    main()
