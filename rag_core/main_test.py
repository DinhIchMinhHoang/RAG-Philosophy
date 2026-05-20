"""
main_test.py - Kịch bản chạy thử toàn bộ RAG pipeline.

Full flow: Load PDF → Chunking → Embedding + Qdrant → RAG Chain → Chat loop.

Cách dùng:
    # Xử lý 1 file cụ thể:
    python rag_core/main_test.py "D:\RAG-Philosophy\data\raw\1706.03762v7.pdf"

    # Xử lý tất cả PDF trong data/raw/ (mặc định):
    python rag_core/main_test.py

    # Bật reranker (Cohere):
    python rag_core/main_test.py --reranker

    # Bật hybrid retrieval (Dense + BM25):
    python rag_core/main_test.py --hybrid

    # Bật reranker + hybrid:
    python rag_core/main_test.py --reranker --hybrid

    # Chạy RAGAS evaluation sau khi chat xong:
    python rag_core/main_test.py --ragas
"""

import argparse
import os
import sys
import logging
os.environ["TOKENIZERS_PARALLELISM"] = "false"

<<<<<<< HEAD
from common.logging_utils import configure_logging, get_logger
from pipeline import build_pipeline, query

=======
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from common.logging_utils import configure_logging, get_logger
from pipeline import build_pipeline, query

>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
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
    Entry point chính với CLI flags để bật/tắt tính năng.

    Cách dùng:
        python rag_core/main_test.py                          # tất cả PDF
        python rag_core/main_test.py path/to/file.pdf        # 1 file cụ thể
        python rag_core/main_test.py --reranker               # bật Cohere reranker
        python rag_core/main_test.py --hybrid                 # bật Dense+BM25
        python rag_core/main_test.py --reranker --hybrid      # bật cả hai
        python rag_core/main_test.py --ragas                  # chạy RAGAS sau chat
    """
<<<<<<< HEAD
    target_pdf: str | None = None
    if len(sys.argv) >= 2:
        target_pdf = sys.argv[1].strip('"').strip("'")
=======
    parser = argparse.ArgumentParser(
        description="RAG Philosophy — CLI test runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "pdf", nargs="?", default=None,
        help="Đường dẫn file PDF cụ thể (bỏ trống = tất cả PDF trong data/raw/)",
    )
    parser.add_argument(
        "--reranker", action="store_true",
        help="Bật Cohere Reranker (cần COHERE_API_KEY trong .env)",
    )
    parser.add_argument(
        "--hybrid", action="store_true",
        help="Bật Hybrid Retrieval (Dense + BM25 + RRF)",
    )
    parser.add_argument(
        "--ragas", action="store_true",
        help="Chạy RAGAS evaluation sau khi kết thúc chat loop",
    )
    args = parser.parse_args()

    # ── Override Config runtime (không cần sửa .env) ─────────────────
    from config import Config
    if args.reranker:
        Config.RERANK_ENABLED = True
        Config.HYBRID_ENABLED = True   # reranker luôn cần hybrid làm candidate pool
        print("✅ Reranker: BẬT (Cohere)")
    if args.hybrid:
        Config.HYBRID_ENABLED = True
        print("✅ Hybrid Retrieval: BẬT (Dense + BM25)")
    if not args.reranker and not args.hybrid:
        mode = "Reranker" if Config.RERANK_ENABLED else ("Hybrid" if Config.HYBRID_ENABLED else "Baseline (Dense only)")
        print(f"ℹ️  Retrieval mode: {mode} (từ .env)")

    target_pdf = args.pdf.strip('"').strip("'") if args.pdf else None
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca

    print("\n🚀 Đang khởi tạo RAG Pipeline...")
    print("   (Lần đầu tải model có thể mất vài phút)\n")

    try:
        artifacts, rag_chain = build_pipeline(target_pdf=target_pdf)
        if rag_chain:
<<<<<<< HEAD
            print(f"Pipeline ready: {artifacts.parent_docs_count} parent docs, {artifacts.child_docs_count} child docs")
=======
            print(f"✅ Pipeline ready: {artifacts.parent_docs_count} parent docs, {artifacts.child_docs_count} child docs")
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
            chat_loop(rag_chain)

        # ── RAGAS evaluation (tuỳ chọn) ───────────────────────────────
        if args.ragas:
            print("\n" + "=" * 60)
            print("  🧪 RAGAS EVALUATION")
            print("=" * 60)
            dataset_path = "data/dataset.json"
            out_path = "data/result.csv"
            records_path = "data/ragas_records.json"
            if not os.path.exists(dataset_path):
                print(f"⚠️  Không tìm thấy dataset: {dataset_path}")
                print("   Tạo file data/dataset.json với format:")
                print('   [{"question": "...", "ground_truth": "..."}]')
            else:
                import subprocess
                cmd = [
                    sys.executable,
                    "rag_core/ragas_eval.py",
                    "--dataset", dataset_path,
                    "--out", out_path,
                    "--records-in", records_path,
                ]
                print(f"▶ Chạy: {' '.join(cmd)}\n")
                subprocess.run(cmd, check=False)

    except FileNotFoundError as e:
        logger.error("❌ %s", e)
        print(f"\n⚠️ Không tìm thấy file. Kiểm tra đường dẫn PDF.")
    except EnvironmentError as e:
        logger.error("❌ %s", e)
        print(f"\n⚠️ Lỗi cấu hình: {e}")
    except Exception as e:
        logger.error("❌ Lỗi không mong muốn: %s", e)
        raise


if __name__ == "__main__":
    main()