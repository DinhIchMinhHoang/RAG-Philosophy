"""
DOCX parser for the RAG pipeline.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import List

import pypandoc
from langchain_core.documents import Document

try:
    from .common.logging_utils import configure_logging, get_logger
    from .common.nonpdf_renderers import _split_priority, render_docx_to_pdf
    from .config import Config
    from .md_parser import _sanitize_and_split
    from .step1_parser import HybridPDFParser
except ImportError:  # pragma: no cover
    from common.logging_utils import configure_logging, get_logger
    from common.nonpdf_renderers import _split_priority, render_docx_to_pdf
    from config import Config
    from md_parser import _sanitize_and_split
    from step1_parser import HybridPDFParser

configure_logging()
logger = get_logger(__name__)

NAMESPACE_DOCX = uuid.uuid5(uuid.NAMESPACE_URL, "docx.parser.rag.uet.edu.vn")


def _magic_check(file_path: str) -> None:
    with open(file_path, "rb") as f:
        header = f.read(4)
    if header[:4] != b"PK\x03\x04":
        raise ValueError(
            "Unsupported file format. Expected .docx (OOXML/ZIP), "
            "but file signature does not match. Please save as .docx first."
        )


def _parse_docx_via_pandoc(
    file_path: str,
    source: str,
    document_id: str,
    pipeline_version: str,
) -> List[Document]:
    markdown = pypandoc.convert_file(
        file_path,
        "markdown",
        format="docx",
        extra_args=["--wrap=none"],
    )
    if not markdown.strip():
        raise ValueError(f"No extractable content from DOCX file: {source}")
    logger.info("[DocxParser] Pandoc success: %d chars", len(markdown))
    return _sanitize_and_split(
        markdown,
        source,
        document_id,
        pipeline_version,
        namespace=NAMESPACE_DOCX,
    )


def _parse_docx_via_ocr(
    file_path: str,
    source: str,
    document_id: str,
    pipeline_version: str,
) -> List[Document]:
    rendered_pdf = render_docx_to_pdf(
        file_path,
        timeout_seconds=Config.OCR_RENDER_TIMEOUT_SECONDS,
        priority=_split_priority(
            Config.OCR_RENDERER_DOCX_PRIORITY,
            default=["soffice", "pandoc"],
        ),
    )
    try:
        ocr_docs = HybridPDFParser().parse_pdf(rendered_pdf)
    finally:
        Path(rendered_pdf).unlink(missing_ok=True)

    markdown = "\n\n".join(
        doc.page_content.strip()
        for doc in ocr_docs
        if doc.page_content and doc.page_content.strip()
    )
    if not markdown.strip():
        raise ValueError("OCR produced empty markdown for DOCX")
    logger.info("[DocxParser] OCR path success: %d chars", len(markdown))
    return _sanitize_and_split(
        markdown,
        source,
        document_id,
        pipeline_version,
        namespace=NAMESPACE_DOCX,
    )


def parse_docx(
    file_path: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    _magic_check(file_path)
    source = os.path.basename(file_path)

    mode = (Config.OCR_NONPDF_MODE or "primary").strip().lower()
    if mode not in {"primary", "strict", "assist"}:
        mode = "primary"

    if Config.OCR_DOCX_ENABLED and mode in {"primary", "strict"}:
        try:
            return _parse_docx_via_ocr(file_path, source, document_id, pipeline_version)
        except Exception as exc:
            if mode == "strict":
                raise ValueError(f"DOCX OCR strict mode failed: {exc}") from exc
            logger.warning("[DocxParser] OCR path failed, fallback to pandoc: %s", exc)

    return _parse_docx_via_pandoc(file_path, source, document_id, pipeline_version)


if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage: python docx_parser.py <file.docx> [document_id] [pipeline_version]")
        sys.exit(1)

    file_path = sys.argv[1]
    doc_id = sys.argv[2] if len(sys.argv) > 2 else "test-document-id"
    pipe_ver = sys.argv[3] if len(sys.argv) > 3 else "v1"

    start = time.time()
    docs = parse_docx(file_path, doc_id, pipe_ver)
    elapsed = time.time() - start

    print(f"Parsed: {len(docs)} pages in {elapsed:.2f}s")
    for doc in docs:
        print(f"--- Page {doc.metadata['page']} ({len(doc.page_content)} chars)")
        print(f"    doc_id: {doc.metadata['doc_id']}")
        print(doc.page_content[:300])
