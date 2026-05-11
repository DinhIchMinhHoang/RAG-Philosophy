"""
main_test.py - Kịch bản chạy thử toàn bộ RAG pipeline.

Full flow: Load PDF → Chunking → Embedding + Qdrant → RAG Chain → Chat loop.

Cách dùng:
    # Xử lý 1 file cụ thể:
    python main_test.py "D:\RAG-Philosophy\data\raw\1706.03762v7.pdf"

    # Xử lý tất cả PDF trong data/raw/ (mặc định):
    python main_test.py
"""

import os
import sys
import logging
os.environ["TOKENIZERS_PARALLELISM"] = "false"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from common.logging_utils import configure_logging, get_logger
from pipeline import build_pipeline, query

configure_logging()
logger = get_logger(__name__)


def chat_loop(rag_chain):
    """
    Vòng lặp chat tương tác — hỏi nhiều câu liên tiếp.
    Gõ 'exit', 'quit' hoặc 'q' để thoát.
    """
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
            result = query(rag_chain, question)

            print(f"\n🤖 Trợ lý:\n{result['answer']}")

            if result["sources"]:
                print(f"\n📚 Nguồn tham khảo:")
                seen = set()
                for src in result["sources"]:
                    key = (src["page"], src["source"])
                    if key not in seen:
                        seen.add(key)
                        filename = os.path.basename(src["source"])
                        print(f"   - {filename}, Trang {src['page']}")

        except Exception as e:
            logger.error(f"❌ Lỗi khi xử lý câu hỏi: {e}")
            print(f"⚠️ Đã xảy ra lỗi: {e}")


def main():
    """
    Entry point chính.

    Cách dùng:
        python main_test.py                                 # tất cả PDF
        python main_test.py path/to/file.pdf               # 1 file cụ thể
    """
    target_pdf: str | None = None
    if len(sys.argv) >= 2:
        target_pdf = sys.argv[1].strip('"').strip("'")

    print("\n🚀 Đang khởi tạo RAG Pipeline...")
    print("   (Lần đầu tải model có thể mất vài phút)\n")

    try:
        artifacts, rag_chain = build_pipeline(target_pdf=target_pdf)
        if rag_chain:
            print(f"Pipeline ready: {artifacts.parent_docs_count} parent docs, {artifacts.child_docs_count} child docs")
            chat_loop(rag_chain)

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        print(f"\n⚠️ Không tìm thấy file. Kiểm tra đường dẫn PDF.")
    except EnvironmentError as e:
        logger.error(f"❌ {e}")
        print(f"\n⚠️ Lỗi cấu hình: {e}")
    except Exception as e:
        logger.error(f"❌ Lỗi không mong muốn: {e}")
        raise


if __name__ == "__main__":
    main()