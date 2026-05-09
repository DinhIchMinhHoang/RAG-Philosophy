from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from langchain_core.documents import Document

from config import Config
from common.logging_utils import configure_logging, get_logger
from common import pdf_utils
from step1_parser import HybridPDFParser
from step2_chunker import chunk_documents
from step3_vector_db import build_vector_db
from step4_generator import setup_rag_chain, ask


logger = get_logger(__name__)


@dataclass(frozen=True)
class PipelineArtifacts:
    retriever: object
    child_docs_count: int
    parent_docs_count: int
    pdf_paths: List[str]


def ingest(target_pdf: Optional[str] = None) -> PipelineArtifacts:
    configure_logging()

    pdf_paths = pdf_utils.collect_pdf_paths(target_pdf, Config.RAW_DIR)
    parser = HybridPDFParser()

    all_child_docs: List[Document] = []
    all_parent_docs: List[Document] = []

    for pdf_path in pdf_paths:
        pages = parser.parse_pdf(pdf_path)
        if not pages:
            logger.warning("No content parsed from %s", pdf_path)
            continue
        child_docs, parent_docs = chunk_documents(pages)
        all_child_docs.extend(child_docs)
        all_parent_docs.extend(parent_docs)

    if not all_child_docs:
        raise ValueError("No documents parsed from PDFs.")

    retriever = build_vector_db(all_child_docs, all_parent_docs)
    return PipelineArtifacts(
        retriever=retriever,
        child_docs_count=len(all_child_docs),
        parent_docs_count=len(all_parent_docs),
        pdf_paths=pdf_paths,
    )


def build_pipeline(target_pdf: Optional[str] = None):
    artifacts = ingest(target_pdf)
    rag_chain = setup_rag_chain(artifacts.retriever)
    return artifacts, rag_chain


def query(rag_chain, question: str) -> dict:
    return ask(rag_chain, question)


# Re-exports for test mocking: tests patch pipeline.xxx names
build_vector_db = build_vector_db
chunk_documents = chunk_documents
setup_rag_chain = setup_rag_chain
HybridPDFParser = HybridPDFParser