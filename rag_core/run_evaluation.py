"""
run_evaluation.py - Batch Evaluation Orchestrator (Real Pipeline).

Kịch bản chạy đánh giá tự động:
  1. Thiết lập Guardrails chống crash C++/SSL/HuggingFace trên Windows.
  2. Load golden_dataset.json.
  3. Khởi tạo pipeline RAG thật (Qdrant + BM25 + Reranker).
  4. Đưa từng câu hỏi vào rag_chain, lấy answer + context thô.
  5. Gọi step5_evaluator.run_ragas_evaluation() để chấm điểm LLM-as-a-Judge.
  6. In bảng kết quả rút gọn ra terminal.

Usage:
  cd rag_core
  python run_evaluation.py
"""

# ══════════════════════════════════════════════════════════════════════════════
# 🚨 KHỐI CẤU HÌNH OFFLINE & CHỐNG CRASH — PHẢI ĐẶT Ở DÒNG ĐẦU TIÊN 🚨
# ══════════════════════════════════════════════════════════════════════════════
import os
import ssl
import sys

# ── Ép HuggingFace Offline (Không tải model qua mạng) ────────────────────────
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"

# ── Chống crash C++ trên Windows (Arrow/OpenMP) ──────────────────────────────
os.environ["ARROW_MIMALLOC"] = "0"
os.environ["ARROW_USER_SIMD_LEVEL"] = "NONE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# ── Vá SSL cho Windows (tránh lỗi certificate verification) ──────────────────
try:
    ssl._create_default_https_context = ssl._create_unverified_context
    ssl.create_default_context = ssl._create_unverified_context
except AttributeError:
    pass

# ── Bật faulthandler để debug segfault ────────────────────────────────────────
import faulthandler
faulthandler.enable()

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS (sau khi guardrails đã được set)
# ══════════════════════════════════════════════════════════════════════════════

import json
import logging
from typing import Any, Dict, List

from config import EvaluationConfig
from step5_evaluator import run_ragas_evaluation

# ── Logging Configuration ─────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-20s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ── Dataset Loading ───────────────────────────────────────────────────────────

def load_golden_dataset(path: str) -> List[Dict[str, str]]:
    """
    Load the golden evaluation dataset from a JSON file.

    Args:
        path: Absolute or relative path to golden_dataset.json.

    Returns:
        List of dicts with 'user_input' and 'reference' keys.

    Raises:
        FileNotFoundError: If the dataset file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    logger.info(f"[Orchestrator] Loading golden dataset from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    logger.info(f"[Orchestrator] Loaded {len(dataset)} evaluation samples.")
    return dataset


# ── Pipeline Evaluation ───────────────────────────────────────────────────────

def evaluate_pipeline(dataset: List[Dict[str, str]]) -> None:
    """
    Run the full evaluation pipeline using the REAL RAG chain.

    For each sample in the golden dataset:
      1. Send user_input through the real RAG pipeline (rag_chain.invoke).
      2. Extract the answer and page_content from retrieved context Documents.
      3. Map all fields into the evaluator-compatible format.
      4. Call run_ragas_evaluation() for LLM-as-a-Judge scoring.

    Args:
        dataset: List of golden Q&A pairs (user_input + reference).
    """
    # ── Khởi tạo RAG Pipeline thật ────────────────────────────────────
    logger.info("[Orchestrator] Đang khởi tạo RAG pipeline thật...")
    from main_test import build_pipeline
    rag_chain = build_pipeline(
        target_pdf=r"D:\RAG-Philosophy\data\raw\Triết_Mác_Lenin.pdf"
    )

    if rag_chain is None:
        logger.error(
            "[Orchestrator] ❌ Không thể khởi tạo pipeline. "
            "Kiểm tra xem thư mục data/raw/ có chứa file PDF không."
        )
        return

    logger.info(f"[Orchestrator] ✅ Pipeline sẵn sàng. Bắt đầu đánh giá {len(dataset)} mẫu...")

    # ── Collect evaluation samples ────────────────────────────────────
    eval_samples: List[Dict[str, Any]] = []

    for i, sample in enumerate(dataset):
        query: str = sample["user_input"]
        reference: str = sample["reference"]

        logger.info(f"[Orchestrator] 📝 Mẫu {i + 1}/{len(dataset)}: {query[:60]}...")

        try:
            # Gọi pipeline RAG thật
            result = rag_chain.invoke({"input": query})

            # Extract answer
            response: str = result.get("answer", "")

            # Extract actual page_content from retrieved context Documents
            retrieved_contexts: List[str] = [
                doc.page_content for doc in result.get("context", [])
            ]

            # Log thông tin sources
            sources = []
            for doc in result.get("context", []):
                src_file = os.path.basename(doc.metadata.get("source", "N/A"))
                src_page = doc.metadata.get("page", "N/A")
                sources.append(f"{src_file}:p{src_page}")

            logger.info(
                f"   → Answer: {response[:80]}..."
                f"\n   → Sources: {', '.join(sources[:5])}"
                f"\n   → Context chunks: {len(retrieved_contexts)}"
            )

            # Map to evaluator format
            eval_samples.append({
                "user_input": query,
                "response": response,
                "retrieved_contexts": retrieved_contexts,
                "reference": reference,
            })

        except Exception as e:
            logger.error(f"[Orchestrator] ❌ Lỗi khi xử lý mẫu {i + 1}: {e}")
            # Vẫn thêm sample với điểm mặc định 0 để không bỏ sót
            eval_samples.append({
                "user_input": query,
                "response": f"[LỖI PIPELINE: {e}]",
                "retrieved_contexts": [],
                "reference": reference,
            })

    logger.info("[Orchestrator] ═══════════════════════════════════════════════")
    logger.info("[Orchestrator] Tất cả mẫu đã xử lý. Bắt đầu chấm điểm LLM-as-a-Judge...")

    # ── Call the LLM-as-a-Judge evaluator ─────────────────────────────
    # Có thể tùy chỉnh các metrics bằng cách truyền các flag:
    #   df = run_ragas_evaluation(eval_samples, 
    #       is_live_chat=False,
    #       use_faithfulness=True,          # Bắt ảo giác
    #       use_answer_relevancy=True,      # Độ phù hợp
    #       use_answer_correctness=True,    # Độ chính xác
    #       use_context_recall=True)        # Khôi phục ngữ cảnh
    # 
    # Ví dụ: Chỉ chạy Faithfulness và AnswerRelevancy:
    #   df = run_ragas_evaluation(eval_samples,
    #       is_live_chat=False,
    #       use_faithfulness=True,
    #       use_answer_relevancy=True,
    #       use_answer_correctness=False,
    #       use_context_recall=False)
    df = run_ragas_evaluation(eval_samples, is_live_chat=False)

    # ── Print final results (bảng rút gọn) ────────────────────────────
    print("\n" + "═" * 70)
    print("📊  KẾT QUẢ ĐÁNH GIÁ RAG PIPELINE (LLM-as-a-Judge)")
    print("═" * 70)

    # Bảng rút gọn: chỉ hiện câu hỏi (50 ký tự) + 3 điểm
    display_cols = ["user_input", "faithfulness", "answer_relevancy"]
    if "context_recall" in df.columns:
        display_cols.append("context_recall")
    if "answer_correctness" in df.columns:
        display_cols.append("answer_correctness")

    df_display = df[display_cols].copy()
    df_display["user_input"] = df_display["user_input"].str[:50] + "..."

    print(df_display.to_string(index=False))

    # Tổng kết trung bình
    print("─" * 70)
    avg_line = "  AVG: "
    for col in ["faithfulness", "answer_relevancy", "context_recall", "answer_correctness"]:
        if col in df.columns:
            avg_line += f"{col}={df[col].mean():.2f}  "
    print(avg_line)

    print("═" * 70)
    print(f"\n📁 Báo cáo chi tiết đã lưu tại: {EvaluationConfig.EVAL_REPORT_PATH}")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main() -> None:
    """Main entry point for the batch evaluation orchestrator."""
    logger.info("[Orchestrator] ══ BATCH EVALUATION PIPELINE (LLM-as-a-Judge) ══")

    # Validate environment
    EvaluationConfig.validate()

    # Load golden dataset
    golden_dataset = load_golden_dataset(EvaluationConfig.EVAL_DATASET_PATH)

    # Run evaluation
    evaluate_pipeline(golden_dataset)

    logger.info("[Orchestrator] ✅ Đánh giá hoàn tất.")


if __name__ == "__main__":
    main()
