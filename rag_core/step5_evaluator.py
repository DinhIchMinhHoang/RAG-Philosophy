"""
step5_evaluator.py - Evaluation Module sử dụng Ragas v0.4.3 (Native LLM-as-a-Judge).

Cách tiếp cận:
  • Thay thế Custom Prompts tiếng Việt bằng thư viện ragas mã nguồn mở.
  • Sử dụng wrapper LangchainLLMWrapper & LangchainEmbeddingsWrapper để tương thích
    với LangChain 0.3.x + Gemini LLM + Harrier Embeddings.
  • Chạy evaluate() với các metrics chuẩn: Faithfulness, AnswerRelevancy, 
    AnswerCorrectness.
  • Export báo cáo CSV và log kết quả trung bình ra console.

Bảo tồn API:
  run_ragas_evaluation(eval_samples, is_live_chat=False) → pd.DataFrame
  Tương thích ngược với code gọi cũ từ main_test.py.
"""

import logging
import os
from typing import Any, Dict, List

import nest_asyncio
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from datasets import Dataset
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import faithfulness, answer_relevancy, answer_correctness, context_recall

from config import EvaluationConfig

# ── Khóa Event Loop (Bắt buộc để tránh crash async) ────────────────────────────
nest_asyncio.apply()

logger = logging.getLogger(__name__)


def run_ragas_evaluation(
    eval_samples: List[Dict[str, Any]],
    is_live_chat: bool = False,
    use_faithfulness: bool = True,
    use_answer_relevancy: bool = True,
    use_answer_correctness: bool = True,
    use_context_recall: bool = True,
) -> pd.DataFrame:
    """
    Chạy đánh giá RAG sử dụng thư viện Ragas v0.4.3 (Native LLM-as-a-Judge).

    Luồng xử lý:
      1. Khởi tạo LLM (Gemini) và Embeddings (Harrier) từ Config.
      2. Bọc chúng bằng LangchainLLMWrapper & LangchainEmbeddingsWrapper
         (yêu cầu của Ragas v0.4+).
      3. Chuyển đổi danh sách eval_samples thành HuggingFace Dataset.
      4. Gọi ragas.evaluate() với các metric được bật (configurable).
      5. Xuất báo cáo CSV và in kết quả trung bình ra console.

    Args:
        eval_samples: Danh sách Dict chứa:
            - user_input (str): Câu hỏi của người dùng.
            - response (str): Câu trả lời từ RAG chain.
            - retrieved_contexts (List[str]): Danh sách ngữ cảnh được tìm thấy.
            - reference (str, optional): Đáp án tham khảo (dùng cho ContextRecall).
        is_live_chat (bool): 
            - True  → Chế độ Live Chat (không có reference, bỏ qua metrics cần reference).
            - False → Chế độ Batch Report (có reference, chạy đầy đủ metrics theo flag).
        use_faithfulness (bool): Bật/tắt Faithfulness metric (Bắt ảo giác). Default: True.
        use_answer_relevancy (bool): Bật/tắt Answer Relevancy metric (Độ phù hợp). Default: True.
        use_answer_correctness (bool): Bật/tắt Answer Correctness metric (Độ chính xác). Default: True.
        use_context_recall (bool): Bật/tắt Context Recall metric (Khôi phục ngữ cảnh). Default: True.

    Returns:
        pd.DataFrame: Bảng kết quả với các cột:
            - user_input, response, reference, contexts
            - faithfulness, answer_relevancy, answer_correctness, context_recall
              (chỉ có các cột của metrics được bật)

    Raises:
        ValueError: Nếu eval_samples rỗng hoặc tất cả metrics đều bị tắt.
        EnvironmentError: Nếu GEMINI_API_KEY không được thiết lập.
    """
    if not eval_samples:
        raise ValueError("eval_samples không được để trống.")

    if not EvaluationConfig.GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY chưa được thiết lập.")

    os.environ["GOOGLE_API_KEY"] = EvaluationConfig.GEMINI_API_KEY

    mode_name = "Live Chat" if is_live_chat else "Batch Report"
    logger.info(
        f"[Evaluator] 🚀 Khởi chạy Ragas Evaluator v0.4.3 — Chế độ: {mode_name}"
    )
    logger.info(f"[Evaluator] Số lượng mẫu cần đánh giá: {len(eval_samples)}")

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 1: Khởi tạo LLM & Embeddings (LangChain 0.3.x)
    # ──────────────────────────────────────────────────────────────────────
    logger.info("[Evaluator] Khởi tạo LLM Evaluator (Gemini)...")
    evaluator_llm = ChatGoogleGenerativeAI(
        model=EvaluationConfig.EVAL_LLM_MODEL,
        temperature=0.0,  # Deterministic scoring
    )

    logger.info(
        f"[Evaluator] Khởi tạo Embedding Evaluator ({EvaluationConfig.EVAL_EMBEDDING_MODEL})..."
    )

    import torch
    # Đặt vào trước đoạn khởi tạo HuggingFaceEmbeddings
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"[Evaluator] Sử dụng thiết bị: {device}")
    
    evaluator_embeddings = HuggingFaceEmbeddings(
    model_name=EvaluationConfig.EVAL_EMBEDDING_MODEL,
    model_kwargs={
        "device": device, # <-- Tự động dùng GPU nếu có
        "trust_remote_code": True,
    },
    )

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 2: Bọc LLM & Embeddings bằng Ragas Wrappers (Bắt buộc v0.4+)
    # ──────────────────────────────────────────────────────────────────────
    logger.info("[Evaluator] Bọc LLM & Embeddings bằng Ragas Wrappers...")
    ragas_llm = LangchainLLMWrapper(evaluator_llm)
    ragas_embeddings = LangchainEmbeddingsWrapper(evaluator_embeddings)

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 3: Chuyển đổi dữ liệu sang HuggingFace Dataset format
    # ──────────────────────────────────────────────────────────────────────
    logger.info("[Evaluator] Chuẩn bị dữ liệu cho Ragas (HuggingFace Dataset)...")

    dataset_dict = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],  # Dùng cho ContextRecall & AnswerCorrectness
    }

    for sample in eval_samples:
        q = sample.get("user_input", "")
        a = sample.get("response", "")
        ctx = sample.get("retrieved_contexts", [])
        ref = sample.get("reference", "")

        dataset_dict["question"].append(q)
        dataset_dict["answer"].append(a)
        dataset_dict["contexts"].append(ctx)  # Ragas yêu cầu contexts là list
        dataset_dict["ground_truth"].append(ref if ref else "")

    # Chuyển dict thành HuggingFace Dataset
    dataset = Dataset.from_dict(dataset_dict)
    logger.info(f"[Evaluator] ✅ Dataset prepared: {len(dataset)} samples")

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 4: Xác định danh sách metrics dựa trên flags (configurable)
    # ──────────────────────────────────────────────────────────────────────
    metrics_to_use = []
    enabled_metrics_names = []

    # Thêm Faithfulness nếu được bật
    if use_faithfulness:
        metrics_to_use.append(faithfulness)
        enabled_metrics_names.append("Faithfulness")

    # Thêm Answer Relevancy nếu được bật
    if use_answer_relevancy:
        metrics_to_use.append(answer_relevancy)
        enabled_metrics_names.append("AnswerRelevancy")

    # Thêm Answer Correctness nếu được bật (yêu cầu reference)
    if use_answer_correctness and not is_live_chat:
        metrics_to_use.append(answer_correctness)
        enabled_metrics_names.append("AnswerCorrectness")
    elif use_answer_correctness and is_live_chat:
        logger.warning(
            "[Evaluator] ⚠️  AnswerCorrectness requires reference (không có trong Live Chat mode)"
        )

    # Thêm Context Recall nếu được bật (yêu cầu reference)
    if use_context_recall and not is_live_chat:
        metrics_to_use.append(context_recall)
        enabled_metrics_names.append("ContextRecall")
    elif use_context_recall and is_live_chat:
        logger.warning(
            "[Evaluator] ⚠️  ContextRecall requires reference (không có trong Live Chat mode)"
        )

    if not metrics_to_use:
        raise ValueError(
            "Tất cả metrics đều bị tắt (disabled). "
            "Bạn phải bật ít nhất 1 metric để chạy evaluation."
        )

    logger.info(
        f"[Evaluator] Metrics được bật: {', '.join(enabled_metrics_names)} "
        f"(Mode: {'Live Chat' if is_live_chat else 'Batch Report'})"
    )

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 5: Chạy Ragas Evaluate
    # ──────────────────────────────────────────────────────────────────────
    logger.info("[Evaluator] Bắt đầu chạy đánh giá Ragas...")

    try:
        result = evaluate(
            dataset=dataset,
            metrics=metrics_to_use,
            llm=ragas_llm,
            embeddings=ragas_embeddings,
            raise_exceptions=False,  # Tránh crash toàn bộ nếu 1 sample lỗi
        )
        logger.info("[Evaluator] ✅ Đánh giá hoàn tất")
    except Exception as e:
        logger.error(f"[Evaluator] ❌ Lỗi khi chạy evaluate: {e}")
        raise

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 6: Chuyển kết quả Ragas thành Pandas DataFrame
    # ──────────────────────────────────────────────────────────────────────
    logger.info("[Evaluator] Chuyển đổi kết quả sang Pandas DataFrame...")

    df = result.to_pandas()

    # Thêm các cột gốc từ eval_samples để bảo toàn metadata
    df.insert(0, "user_input", dataset_dict["question"])
    df.insert(1, "response", dataset_dict["answer"])
    df.insert(2, "retrieved_contexts", dataset_dict["contexts"])
    df.insert(3, "reference", dataset_dict["ground_truth"])

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 7: Xuất báo cáo CSV
    # ──────────────────────────────────────────────────────────────────────
    report_path = EvaluationConfig.EVAL_REPORT_PATH
    df.to_csv(report_path, index=False, encoding="utf-8-sig")
    logger.info(f"[Evaluator] ✅ Báo cáo đã lưu tại: {report_path}")

    # ──────────────────────────────────────────────────────────────────────
    # BƯỚC 8: Log kết quả trung bình (Average Scores) — chỉ show metrics được bật
    # ──────────────────────────────────────────────────────────────────────
    logger.info("[Evaluator] ── TỔNG KẾT ĐIỂM TRUNG BÌNH ──")

    # Định nghĩa mapping metric columns → display names
    metric_names_map = {
        "faithfulness": "Faithfulness (Bắt ảo giác)",
        "answer_relevancy": "Answer Relevancy (Độ phù hợp)",
        "answer_correctness": "Answer Correctness (Độ chính xác)",
        "context_recall": "Context Recall (Khôi phục ngữ cảnh)",
    }

    # Log kết quả cho từng metric được bật
    for metric_col, metric_label in metric_names_map.items():
        if metric_col in df.columns:
            valid_scores = df[metric_col].dropna()
            if len(valid_scores) > 0:
                avg_score = valid_scores.mean()
                logger.info(f"  > {metric_label}: {avg_score:.4f} (n={len(valid_scores)})")

    # In bảng kết quả ra console
    print("\n" + "=" * 70)
    print("📊 RAGAS EVALUATION RESULTS")
    print("=" * 70)
    for metric_col, metric_label in metric_names_map.items():
        if metric_col in df.columns:
            valid_scores = df[metric_col].dropna()
            if len(valid_scores) > 0:
                avg_score = valid_scores.mean()
                print(f"  {metric_label:<40} {avg_score:.4f}")
    print("=" * 70 + "\n")

    return df


# ── Self-test block ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import os as _os

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    print("\n🧪 Testing Ragas Evaluator Module (v0.4.3)...")
    print("=" * 70)

    # Tạo sample dữ liệu test
    test_samples = [
        {
            "user_input": "Triết học Mác-Lênin là gì?",
            "response": (
                "Triết học Mác-Lênin là một hệ thống triết học kết hợp giữa "
                "chủ nghĩa duy vật biện chứng của Marx và những phát triển lý thuyết "
                "do Lenin đóng góp. Nó dựa trên các nguyên tắc cơ bản về vật chất, "
                "phát triển và xung đột giai cấp."
            ),
            "retrieved_contexts": [
                "Triết học Mác-Lênin là nền tảng của thế giới quan khoa học "
                "của giai cấp công nhân.",
                "Nó kết hợp các nguyên tắc duy vật biện chứng của Marx với "
                "những phát triển lý thuyết của Lenin về chủ nghĩa Lênin.",
            ],
            "reference": (
                "Triết học Mác-Lênin là sự kết hợp của chủ nghĩa duy vật biện chứng "
                "Marx và những đóng góp lý thuyết của Lenin về chủ nghĩa Lênin."
            ),
        }
    ]

    try:
        print("\n[Test 1] Running evaluation (Batch Report mode - tất cả metrics)...")
        df_result = run_ragas_evaluation(test_samples, is_live_chat=False)
        print(f"\n✅ Test 1 passed! Results shape: {df_result.shape}")
        print(f"Columns: {list(df_result.columns)}")

        print("\n" + "=" * 70)
        print("\n[Test 2] Running evaluation (chỉ Faithfulness + AnswerRelevancy)...")
        df_result2 = run_ragas_evaluation(
            test_samples,
            is_live_chat=False,
            use_faithfulness=True,
            use_answer_relevancy=True,
            use_answer_correctness=False,  # Tắt
            use_context_recall=False,      # Tắt
        )
        print(f"\n✅ Test 2 passed! Results shape: {df_result2.shape}")
        print(f"Columns: {list(df_result2.columns)}")

        print("\n" + "=" * 70)
        print("\n[Test 3] Running evaluation (Live Chat mode)...")
        test_samples_live = [{
            "user_input": test_samples[0]["user_input"],
            "response": test_samples[0]["response"],
            "retrieved_contexts": test_samples[0]["retrieved_contexts"],
            "reference": None,  # Live Chat không có reference
        }]
        df_result3 = run_ragas_evaluation(
            test_samples_live,
            is_live_chat=True
        )
        print(f"\n✅ Test 3 passed! Results shape: {df_result3.shape}")
        print(f"Columns: {list(df_result3.columns)}")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)