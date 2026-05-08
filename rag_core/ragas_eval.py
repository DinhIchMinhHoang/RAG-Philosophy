"""
ragas_eval.py - Run RAGAS evaluation on rag_core pipeline.

Usage:
    python rag_core/ragas_eval.py --dataset data/dataset.json --out data/result.csv
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from typing import List, Dict, Any

import pandas as pd
from datasets import Dataset
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.run_config import RunConfig

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

from config import Config
from step1_parser import HybridPDFParser
from step2_chunker import chunk_documents
from step3_vector_db import build_vector_db
from step4_generator import SYSTEM_PROMPT


logger = logging.getLogger(__name__)


_CITATION_PATTERN = re.compile(r"\s*\[cite:\s*\d+\]\s*", re.IGNORECASE)


def _strip_citations(text: str) -> str:
    """Remove citation tokens like [cite: 4]."""
    if not text:
        return ""
    return _CITATION_PATTERN.sub(" ", text).strip()


class SafeAsyncChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    async def _agenerate(self, *args: Any, **kwargs: Any):
        kwargs.pop("temperature", None)
        return await super()._agenerate(*args, **kwargs)


def _load_dataset(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Dataset must be a JSON array.")
    return data


def _build_retriever() -> Any:
    """Build retriever from all PDFs in Config.RAW_DIR."""
    pdf_files = [
        os.path.join(Config.RAW_DIR, f)
        for f in os.listdir(Config.RAW_DIR)
        if f.lower().endswith(".pdf")
    ]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {Config.RAW_DIR}")

    parser = HybridPDFParser()
    all_child_docs: List[Document] = []
    all_parent_docs: List[Document] = []

    for pdf_path in pdf_files:
        pages = parser.parse_pdf(pdf_path)
        if not pages:
            continue
        child_docs, parent_docs = chunk_documents(pages)
        all_child_docs.extend(child_docs)
        all_parent_docs.extend(parent_docs)

    if not all_child_docs:
        raise ValueError("No documents parsed from PDFs.")

    return build_vector_db(all_child_docs, all_parent_docs)


def _build_llm() -> ChatGoogleGenerativeAI:
    if not Config.GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is not set.")
    return SafeAsyncChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        temperature=0.2,
        google_api_key=Config.GEMINI_API_KEY,
    )


def _build_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": Config.DEVICE,
            "trust_remote_code": True,
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


def _generate_answer(llm: ChatGoogleGenerativeAI, question: str, contexts: List[str]) -> str:
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
    llm: ChatGoogleGenerativeAI,
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

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
    llm = _build_llm()
    embeddings = _build_embeddings()

    if args.records_in:
        records = _load_records(args.records_in)
        logger.info(f"Loaded evaluation records from {args.records_in}")
    else:
        dataset = _load_dataset(args.dataset)
        retriever = _build_retriever()
        logger.info("Preparing evaluation records...")
        records = _prepare_records(dataset, retriever, llm, limit=args.limit)
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
        llm=llm,
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
