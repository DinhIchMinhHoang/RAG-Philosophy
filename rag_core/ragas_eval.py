"""
ragas_eval.py - Run RAGAS evaluation on rag_core pipeline.

Usage:
    python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from typing import List, Dict, Any

import fitz
import pandas as pd
import torch
from datasets import Dataset
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from ragas.llms import LangchainLLMWrapper


from ragas.run_config import RunConfig

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

from config import Config
from common.logging_utils import configure_logging, get_logger
from common.embeddings import get_embeddings
from pipeline import ingest
from step4_generator import SYSTEM_PROMPT

configure_logging()
logger = get_logger(__name__)


_CITATION_PATTERN = re.compile(r"\s*\[cite:\s*\d+\]\s*", re.IGNORECASE)
_RAGAS_LLM_MODEL = "deepseek-v4-flash"


def _strip_citations(text: str) -> str:
    """Remove citation tokens like [cite: 4]."""
    if not text:
        return ""
    return _CITATION_PATTERN.sub(" ", text).strip()


class _RateLimitedChatOpenAI(BaseChatModel):
    """Caps concurrent async LLM calls to avoid 429 rate limits."""

    def __init__(self, llm: ChatOpenAI, max_concurrency: int = 3):
        super().__init__()
        self._llm = llm
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def _agenerate(self, *args: Any, **kwargs: Any) -> Any:
        async with self._semaphore:
            return await self._llm._agenerate(*args, **kwargs)

    def _generate(self, *args: Any, **kwargs: Any) -> Any:
        return self._llm._generate(*args, **kwargs)

    @property
    def _llm_type(self) -> str:
        return self._llm._llm_type

    def bind_tools(self, *args: Any, **kwargs: Any) -> Any:
        return self._llm.bind_tools(*args, **kwargs)

    def with_structured_output(self, *args: Any, **kwargs: Any) -> Any:
        return self._llm.with_structured_output(*args, **kwargs)


def _load_dataset(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Dataset must be a JSON array.")
    return data


def _build_retriever() -> Any:
    """Build retriever from all PDFs in Config.RAW_DIR."""
    artifacts = ingest()
    return artifacts.retriever


def _build_llm() -> ChatOpenAI:
    if not Config.OPENCODE_API_KEY:
        raise EnvironmentError("OPENCODE_API_KEY is not set.")
    logger.info(f"Using RAGAS eval LLM model: {_RAGAS_LLM_MODEL}")
    return ChatOpenAI(
        model=_RAGAS_LLM_MODEL,
        openai_api_key=Config.OPENCODE_API_KEY,
        openai_api_base=Config.OPENCODE_API_BASE,
        temperature=0.2,
    )


def _resolve_eval_embedding_device() -> str:
    configured_device = (Config.DEVICE or "cpu").strip().lower()
    if configured_device == "auto":
        if torch.cuda.is_available():
            return "cuda"
        raise RuntimeError(
            "RAGAS eval requires GPU embeddings, but EMBEDDING_DEVICE=auto "
            "could not resolve to CUDA because torch.cuda.is_available() is false."
        )

    if configured_device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError(
            f"RAGAS eval requires GPU embeddings, but EMBEDDING_DEVICE={Config.DEVICE!r} "
            "was requested and torch.cuda.is_available() is false."
        )

    return configured_device


def _build_embeddings() -> Any:
    device = _resolve_eval_embedding_device()
    logger.info(f"Using RAGAS eval embeddings: model={Config.EMBEDDING_MODEL_NAME}, device={device}")
    return get_embeddings(model_name=Config.EMBEDDING_MODEL_NAME, device=device)


def _generate_answer(llm: ChatOpenAI, question: str, contexts: List[str]) -> str:
    context_text = "\n\n---\n\n".join(contexts)
    messages = [
        ("system", SYSTEM_PROMPT.format(context=context_text)),
        ("human", question),
    ]
    response = llm.invoke(messages)
    return response.content or ""


def _prepare_records(
    dataset: List[Dict[str, Any]],
    retriever: Any,
    llm: ChatOpenAI,
    limit: int | None = None,
) -> Dict[str, List[Any]]:
    records: Dict[str, List[Any]] = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    items = dataset[:limit] if limit else dataset
    for idx, item in enumerate(items, start=1):
        question = (item.get("question") or "").strip()
        ground_truth = (item.get("ground_truth") or "").strip()
        if not question or not ground_truth:
            logger.warning(f"Skipping item {idx} due to missing fields.")
            continue

        docs = retriever.invoke(question)
        contexts = [doc.page_content for doc in docs] if docs else []

        answer = _generate_answer(llm, question, contexts)

        records["question"].append(question)
        records["answer"].append(_strip_citations(answer))
        records["contexts"].append(contexts)
        records["ground_truth"].append(_strip_citations(ground_truth))

    return records


def _load_records(path: str) -> Dict[str, List[Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Records file must be a JSON object.")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation.")
    parser.add_argument("--dataset", required=True, help="Path to dataset JSON")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of items")
    parser.add_argument(
        "--records-in",
        default=None,
        help="Path to cached evaluation records JSON",
    )
    args = parser.parse_args()

    records_path = os.path.join(Config.DATA_DIR, "ragas_records.json")
    raw_llm = _build_llm()
    limited_llm = _RateLimitedChatOpenAI(raw_llm, max_concurrency=Config.RAGAS_MAX_CONCURRENCY)
    judge = LangchainLLMWrapper(limited_llm)
    embeddings = _build_embeddings()

    if args.records_in:
        records = _load_records(args.records_in)
        logger.info(f"Loaded evaluation records from {args.records_in}")
    else:
        dataset = _load_dataset(args.dataset)
        retriever = _build_retriever()
        logger.info("Preparing evaluation records...")
        records = _prepare_records(dataset, retriever, raw_llm, limit=args.limit)
        if records.get("question"):
            os.makedirs(os.path.dirname(records_path), exist_ok=True)
            with open(records_path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved evaluation records to {records_path}")

    if not records["question"]:
        raise ValueError("No valid records to evaluate.")

    logger.info("Running RAGAS evaluation...")
    dataset_for_evaluation = Dataset.from_dict(records)
    result = evaluate(
        dataset_for_evaluation,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=judge,
        embeddings=embeddings,
        run_config=RunConfig(max_workers=1),
    )

    df = result.to_pandas()

    metric_cols = [
        col for col in df.columns
        if col in {"faithfulness", "answer_relevancy", "context_precision", "context_recall"}
    ]
    summary = {col: df[col].mean() for col in metric_cols}
    summary["question"] = "__mean__"

    df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)

    logger.info(f"Saved RAGAS results to {args.out}")


if __name__ == "__main__":
    main()
