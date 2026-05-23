"""
docx_parser.py — DOCX Parser for RAG pipeline (Pandoc-based, skip images).

Pipeline:
  1. Magic check (PK\x03\x04 = ZIP/OOXML)
  2. pypandoc.convert() → Markdown (images skipped)
  3. Reuse _sanitize_and_split() from md_parser pipeline
  4. Return List[Document] with deterministic UUIDv5
"""

from __future__ import annotations

import os
import uuid
from typing import List

import pypandoc
from langchain_core.documents import Document

try:
    from .common.logging_utils import configure_logging, get_logger
    from .md_parser import _sanitize_and_split
except ImportError:  # pragma: no cover
    from common.logging_utils import configure_logging, get_logger
    from md_parser import _sanitize_and_split

configure_logging()
logger = get_logger(__name__)

# Namespace cố định cho DOCX parser
NAMESPACE_DOCX = uuid.uuid5(uuid.NAMESPACE_URL, "docx.parser.rag.uet.edu.vn")


# =====================================================================
#  MAGIC CHECK
# =====================================================================

def _magic_check(file_path: str) -> None:
    """Validate file is DOCX by checking ZIP/OOXML magic bytes."""
    with open(file_path, 'rb') as f:
        header = f.read(4)
    if header[:4] != b'PK\x03\x04':
        raise ValueError(
            "Unsupported file format. Expected .docx (OOXML/ZIP), "
            "but file signature does not match. Please save as .docx first."
        )


# =====================================================================
#  PUBLIC API
# =====================================================================

def parse_docx(
    file_path: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    """
    Entry point — Parse DOCX → List[Document] via Pandoc.

    Images are skipped (not OCR'd). Text, tables, math, footnotes,
    headers/footers are preserved in Markdown output.

    Args:
        file_path: Absolute path to .docx file.
        document_id: Unique document ID (from upload contract).
        pipeline_version: Pipeline version string (e.g., "v1").

    Returns:
        List[Document] with metadata {source, page, doc_id}.

    Raises:
        ValueError: If file is not valid DOCX or has no extractable content.
    """
    _magic_check(file_path)
    source = os.path.basename(file_path)

    # Convert DOCX → Markdown via Pandoc
    markdown = pypandoc.convert_file(
        file_path,
        'markdown',
        format='docx',
        extra_args=['--wrap=none'],
    )

    if not markdown.strip():
        raise ValueError(f"No extractable content from DOCX file: {source}")

    logger.info("[DocxParser] Pandoc success: %d chars", len(markdown))

    # Reuse MD parser pipeline: sanitize + split by headings
    return _sanitize_and_split(markdown, source, document_id, pipeline_version, namespace=NAMESPACE_DOCX)


# =====================================================================
#  SELF-TEST
# =====================================================================

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
