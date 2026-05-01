"""
main_test.py - Kịch bản chạy thử toàn bộ RAG pipeline.

Full flow: Load PDF → Chunking → Embedding + Qdrant → RAG Chain → Chat loop.
"""

import os
import glob
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def build_pipeline():
    """
    Xây dựng toàn bộ pipeline RAG từ đầu đến cuối.
    Hỗ trợ Incremental Processing: Quét và xử lý file PDF mới trong data/raw.
    """
    from config import Config
    from step1_loader import DocumentAggregator
    from step2_chunker import hierarchical_chunking, save_chunks
    from step3_vector_db import ingest_into_qdrant, get_retriever
    from step4_generator import setup_rag_chain

    # Lấy danh sách tất cả file PDF trong thư mục raw
    pdf_files = glob.glob(os.path.join(Config.RAW_DIR, "*.pdf"))
    
    if not pdf_files:
        print("⚠️ Không tìm thấy file PDF nào trong data/raw/.")
        return None

    parser = DocumentAggregator()
    all_child_chunks = []

    print(f"\n🔍 Đang kiểm tra và xử lý {len(pdf_files)} file PDF...")
    
    for pdf_path in pdf_files:
        source_name = os.path.basename(pdf_path)
        print(f"\n--- Đang kiểm tra: {source_name} ---")
        
        # ── Step 1: Load & Parse PDF ──────────────────────────────
        md_text = parser.parse_doc(pdf_path)
        
        if md_text is None:
            # File đã được xử lý -> Hàm parse_doc đã tự in log "Bỏ qua file cũ"
            continue

        # Lưu Markdown
        parser.save_markdown(md_text, source_name)
        
        # ── Step 2: Chunking ──────────────────────────────────────
        print("✂️  Đang thực hiện Hierarchical Chunking...")
        parents, children = hierarchical_chunking(
            markdown_text=md_text,
            source_name=source_name,
        )
        
        # Lưu Parent Chunks ra JSON
        print(f"💾 Đang lưu Parent Chunks...")
        save_chunks(parents, children, source_name)
        
        # Thu thập các Child Chunks mới để nhúng vector
        all_child_chunks.extend(children)

    # ── Step 3: Embedding + Qdrant ────────────────────────────
    # Nếu có chunk mới, tiến hành nhúng. Ngược lại, thông báo bỏ qua.
    if all_child_chunks:
        print(f"\n🚀 Đang nhúng {len(all_child_chunks)} Child Chunks mới vào Qdrant...")
        vectorstore = ingest_into_qdrant(all_child_chunks)
        retriever = get_retriever(vectorstore)
    else:
        print("\n✅ Tất cả file đã được xử lý từ trước. Bỏ qua bước Embedding.")
        # Khởi tạo retriever từ vectorstore hiện có (Yêu cầu Qdrant phải lưu persistent)
        # Tạm thời gọi get_retriever với vectorstore trống nếu :memory:, hoặc tải lại từ Qdrant
        # (Để dùng được lâu dài, cần set Config.QDRANT_LOCATION trỏ vào ổ cứng)
        from langchain_qdrant import QdrantVectorStore
        from step3_vector_db import get_embeddings
        embeddings = get_embeddings()
        
        # Thử load lại vector store từ ổ cứng
        vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            collection_name=Config.QDRANT_COLLECTION,
            path=Config.QDRANT_PATH,
        )
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
        rag_chain = build_pipeline()
        if rag_chain:
            chat_loop(rag_chain)

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        print(f"\n⚠️ Không tìm thấy file PDF. Kiểm tra thư mục data/raw/.")
    except EnvironmentError as e:
        logger.error(f"❌ {e}")
        print(f"\n⚠️ Lỗi cấu hình: {e}")
    except Exception as e:
        logger.error(f"❌ Lỗi không mong muốn: {e}")
        raise


if __name__ == "__main__":
    main()
