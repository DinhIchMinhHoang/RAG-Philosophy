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
import glob
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def build_pipeline(target_pdf: str | None = None):
    """
    Xây dựng toàn bộ pipeline RAG từ đầu đến cuối.

    Args:
        target_pdf: Đường dẫn tuyệt đối tới 1 file PDF cụ thể.
                    Nếu None → quét tất cả PDF trong Config.RAW_DIR.

    Returns:
        RAG chain sẵn sàng dùng, hoặc None nếu không có dữ liệu.
    """
    from config import Config
    from step1_parser import HybridPDFParser
    from step2_chunker import chunk_documents
    from step3_vector_db import build_vector_db
    from step4_generator import setup_rag_chain

    # ── Xác định danh sách file cần xử lý ───────────────────────────
    if target_pdf:
        if not os.path.isfile(target_pdf):
            print(f"❌ Không tìm thấy file: {target_pdf}")
            return None
        pdf_files = [target_pdf]
        print(f"\n📄 Chế độ: 1 file — {os.path.basename(target_pdf)}")
    else:
        pdf_files = glob.glob(os.path.join(Config.RAW_DIR, "*.pdf"))
        if not pdf_files:
            print("⚠️ Không tìm thấy file PDF nào trong data/raw/.")
            return None
        print(f"\n📂 Chế độ: toàn bộ thư mục — {len(pdf_files)} file PDF")

    # ── Parse → Chunk ────────────────────────────────────────────────
    parser = HybridPDFParser()
    all_child_docs: list = []
    all_parent_docs: list = []

    print(f"\n{'='*60}")
    for pdf_path in pdf_files:
        source_name = os.path.basename(pdf_path)
        print(f"\n📖 Đang xử lý: {source_name}")
        print(f"{'─'*60}")

        # ── Step 1: Parse PDF → List[Document] ───────────────────────
        print("   [Step 1] Parsing PDF...")
        pages = parser.parse_pdf(pdf_path)

        if not pages:
            print(f"   ⏭️  Không có nội dung. Bỏ qua.")
            continue

        print(f"   [Step 1] ✅ {len(pages)} trang")

        # ── Step 2: Parent-Child Chunking ─────────────────────────────
        print("   [Step 2] Chunking...")
        child_docs, parent_docs = chunk_documents(pages)
        print(f"   [Step 2] ✅ {len(parent_docs)} parents, {len(child_docs)} children")

        all_child_docs.extend(child_docs)
        all_parent_docs.extend(parent_docs)

    print(f"\n{'='*60}")

    # ── Step 3: Build Vector DB ───────────────────────────────────────
    if not all_child_docs:
        print("⚠️ Không có dữ liệu để xây dựng vector DB.")
        return None

    print(f"\n[Step 3] Đang xây dựng vector DB...")
    print(f"         {len(all_child_docs)} child docs | {len(all_parent_docs)} parent docs")
    retriever = build_vector_db(all_child_docs, all_parent_docs)

    # ── Step 4: RAG Chain ─────────────────────────────────────────────
    print(f"\n[Step 4] Đang khởi tạo RAG chain...")
    rag_chain = setup_rag_chain(retriever)

    print(f"\n{'='*60}")
    print("✅ Pipeline sẵn sàng!")
    print(f"{'='*60}")
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
    # Đọc argument dòng lệnh (tuỳ chọn)
    target_pdf: str | None = None
    if len(sys.argv) >= 2:
        target_pdf = sys.argv[1].strip('"').strip("'")

    print("\n🚀 Đang khởi tạo RAG Pipeline...")
    print("   (Lần đầu tải model có thể mất vài phút)\n")

    try:
        rag_chain = build_pipeline(target_pdf=target_pdf)
        if rag_chain:
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
