"""
md_parser.py — Markdown Parser for RAG pipeline.

Pipeline:
  1. Read .md file as UTF-8 text
  2. Strip BOM (\ufeff) from Windows Notepad
  3. Apply MarkdownSanitizer.sanitize() (reuse from step1_parser)
  4. Split by headings using MarkdownHeaderTextSplitter
  5. Return List[Document] with deterministic UUIDv5
"""

from __future__ import annotations

import os
import uuid
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

try:
    from .common.logging_utils import configure_logging, get_logger
    from .step1_parser import MarkdownSanitizer
except ImportError:  # pragma: no cover
    from common.logging_utils import configure_logging, get_logger
    from step1_parser import MarkdownSanitizer

configure_logging()
logger = get_logger(__name__)

# Namespace cố định cho Markdown parser
NAMESPACE_MD = uuid.uuid5(uuid.NAMESPACE_URL, "md.parser.rag.uet.edu.vn")


# =====================================================================
#  SANITIZE + SPLIT → List[Document]
# =====================================================================

def _sanitize_and_split(
    markdown: str,
    source: str,
    document_id: str,
    pipeline_version: str,
    namespace: uuid.UUID = NAMESPACE_MD,
) -> List[Document]:
    """
    Sanitize Markdown → Split by headings → List[Document].
    KHÔNG pre-chunk — để chunk_documents() xử lý parent/child splitting.

    Args:
        namespace: UUID namespace deterministic (NAMESPACE_MD/HTML/DOCX)

    UUIDv5 deterministic với {document_id}_{pipeline_version} → idempotent reindex.
    """
    # Step 1: Sanitize (reuse từ PDF pipeline)
    clean_md = MarkdownSanitizer.sanitize(markdown)
    if not clean_md:
        raise ValueError(f"No extractable content from Markdown file: {source}")

    # Step 2: Split by headings (6 cấp)
    headers_to_split_on = [
        ("#", "Header-1"),
        ("##", "Header-2"),
        ("###", "Header-3"),
        ("####", "Header-4"),
        ("#####", "Header-5"),
        ("######", "Header-6"),
    ]

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )

    try:
        md_splits = md_splitter.split_text(clean_md)
        from langchain_core.documents import Document as LCDoc
        md_docs = [LCDoc(page_content=chunk.page_content, metadata=chunk.metadata) for chunk in md_splits]
    except Exception as exc:
        logger.warning("[MdParser] MarkdownHeaderTextSplitter failed: %s. Using raw content.", exc)
        md_docs = [Document(page_content=clean_md, metadata={})]

    # Step 3: Build Documents with deterministic UUIDv5
    documents = []
    for chunk_idx, doc in enumerate(md_docs):
        content = doc.page_content.strip()
        if not content:
            continue

        doc_id = str(uuid.uuid5(
            namespace,
            f"{document_id}_{pipeline_version}_{chunk_idx}"
        ))
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": source,
                    "page": chunk_idx + 1,
                    "doc_id": doc_id,
                    **doc.metadata,
                }
            )
        )

    # Fallback: nếu không có document nào được tạo
    if not documents:
        doc_id = str(uuid.uuid5(
            namespace,
            f"{document_id}_{pipeline_version}_0"
        ))
        documents.append(
            Document(
                page_content=clean_md,
                metadata={
                    "source": source,
                    "page": 1,
                    "doc_id": doc_id,
                }
            )
        )

    logger.info(
        "[MdParser] → %d Document objects from %s (document_id=%s)",
        len(documents), source, document_id,
    )
    return documents


# =====================================================================
#  PUBLIC API
# =====================================================================

def parse_md(
    file_path: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    """
    Entry point — Parse Markdown → List[Document].

    Args:
        file_path: Absolute path to .md file.
        document_id: Unique document ID (from upload contract).
        pipeline_version: Pipeline version string (e.g., "v1").

    Returns:
        List[Document] with metadata {source, page, doc_id}.

    Raises:
        ValueError: If file is empty or has no extractable content.
    """
    source = os.path.basename(file_path)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        markdown = f.read().lstrip('\ufeff')  # Strip BOM from Windows Notepad

    if not markdown.strip():
        raise ValueError(f"Empty Markdown file: {source}")

    return _sanitize_and_split(markdown, source, document_id, pipeline_version)


# =====================================================================
#  SELF-TEST
# =====================================================================

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage: python md_parser.py <file.md> [document_id] [pipeline_version]")
        sys.exit(1)

    file_path = sys.argv[1]
    doc_id = sys.argv[2] if len(sys.argv) > 2 else "test-document-id"
    pipe_ver = sys.argv[3] if len(sys.argv) > 3 else "v1"

    start = time.time()
    docs = parse_md(file_path, doc_id, pipe_ver)
    elapsed = time.time() - start

    print(f"Parsed: {len(docs)} pages in {elapsed:.2f}s")
    for doc in docs:
        print(f"--- Page {doc.metadata['page']} ({len(doc.page_content)} chars)")
        print(f"    doc_id: {doc.metadata['doc_id']}")
        print(doc.page_content[:300])
