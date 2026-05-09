from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import langchain_core.documents
import rag_core.pipeline


@dataclass(frozen=True)
class PipelineArtifacts:
    retriever: object
    child_docs_count: int
    parent_docs_count: int
    pdf_paths: List[str]


def ingest(target_pdf: Optional[str] = None) -> PipelineArtifacts:
    from rag_core.common.logging_utils import configure_logging, get_logger
    from rag_core import config as _config
    from rag_core.common import pdf_utils as _pdf_utils
    from rag_core import step1_parser
    from rag_core import step2_chunker
    from rag_core import step3_vector_db

    logger = get_logger(__name__)
    configure_logging()

    pdf_paths = rag_core.pipeline.collect_pdf_paths(target_pdf, _config.Config.RAW_DIR)
    parser = rag_core.pipeline.HybridPDFParser()

    all_child_docs: List[langchain_core.documents.Document] = []
    all_parent_docs: List[langchain_core.documents.Document] = []

    for pdf_path in pdf_paths:
        pages = parser.parse_pdf(pdf_path)
        if not pages:
            logger.warning("No content parsed from %s", pdf_path)
            continue
        child_docs, parent_docs = rag_core.pipeline.chunk_documents(pages)
        all_child_docs.extend(child_docs)
        all_parent_docs.extend(parent_docs)

    if not all_child_docs:
        raise ValueError("No documents parsed from PDFs.")

    retriever = rag_core.pipeline.build_vector_db(all_child_docs, all_parent_docs)
    return PipelineArtifacts(
        retriever=retriever,
        child_docs_count=len(all_child_docs),
        parent_docs_count=len(all_parent_docs),
        pdf_paths=pdf_paths,
    )


def build_pipeline(target_pdf: Optional[str] = None):
    artifacts = rag_core.pipeline.ingest(target_pdf)
    rag_chain = rag_core.pipeline.setup_rag_chain(artifacts.retriever)
    return artifacts, rag_chain


def query(rag_chain, question: str) -> dict:
    from rag_core import step4_generator
    return step4_generator.ask(rag_chain, question)


def collect_pdf_paths(*args, **kwargs):
    from rag_core.common.pdf_utils import collect_pdf_paths as _fn
    return _fn(*args, **kwargs)


def chunk_documents(*args, **kwargs):
    from rag_core.step2_chunker import chunk_documents as _fn
    return _fn(*args, **kwargs)


def build_vector_db(*args, **kwargs):
    from rag_core.step3_vector_db import build_vector_db as _fn
    return _fn(*args, **kwargs)


class HybridPDFParser:
    def __init__(self):
        from rag_core.step1_parser import HybridPDFParser as _cls
        self._inner = _cls()

    def parse_pdf(self, *args, **kwargs):
        return self._inner.parse_pdf(*args, **kwargs)


def setup_rag_chain(*args, **kwargs):
    from rag_core.step4_generator import setup_rag_chain as _fn
    return _fn(*args, **kwargs)