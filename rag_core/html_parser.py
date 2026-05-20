"""
html_parser.py — HTML Parser for RAG pipeline.

Pipeline:
  1. Flexible magic check (BSoup detect <html> tag)
  2. Primary: Trafilatura.extract(output_format='markdown')
  3. Fallback: BeautifulSoup + Readability
  4. Split by headings ONLY (virtual pages) — chunker handles parent/child splitting
  5. Deterministic UUIDv5 với {document_id}_{pipeline_version} → idempotent reindex
"""

from __future__ import annotations

import os
import uuid
from typing import List, Optional

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

# Namespace cố định cho HTML parser (tương tự NAMESPACE_RAG trong chunker)
NAMESPACE_HTML = uuid.uuid5(uuid.NAMESPACE_URL, "html.parser.rag.uet.edu.vn")


# =====================================================================
#  FLEXIBLE MAGIC CHECK
# =====================================================================

def _magic_check(file_path: str) -> None:
    """
    Validate file is HTML bằng BSoup detection.
    Nới lỏng hơn hardcode <!doctype html — chấp nhận cả file có XML header dài.
    """
    with open(file_path, 'rb') as f:
        content = f.read(8192)  # Đọc 8KB để cover cả XML header dài

    try:
        text = content.decode('utf-8', errors='ignore').lower()
    except Exception:
        raise ValueError("Cannot read file as text")

    # Fast check: detect HTML tags
    if '<html' in text or '<!doctype' in text:
        return

    # Fallback: try BSoup parse
    from bs4 import BeautifulSoup
    try:
        soup = BeautifulSoup(content, 'html.parser')
        if not soup.find(['html', 'head', 'body']):
            raise ValueError("No HTML structure detected")
    except ValueError:
        raise
    except Exception:
        raise ValueError(
            "Unsupported file format. Expected .html/.htm, "
            "but file signature does not match."
        )


# =====================================================================
#  PRIMARY: TRAFILATURA
# =====================================================================

def _extract_with_trafilatura(html: str) -> Optional[str]:
    """
    Primary extraction using Trafilatura.
    Returns Markdown or None if extraction fails or content too short.
    """
    import trafilatura

    result = trafilatura.extract(
        html,
        include_tables=True,
        include_images=False,
        output_format='markdown',
        favor_precision=True,
    )

    if result and len(result.strip()) > 100:
        return result
    return None


# =====================================================================
#  FALLBACK: BEAUTIFULSOUP + READABILITY
# =====================================================================

def _extract_with_bsoup_fallback(html: str) -> Optional[str]:
    """
    Fallback extraction using BeautifulSoup + Readability.
    Returns Markdown-like text or None if extraction fails.
    """
    from bs4 import BeautifulSoup

    # Try Readability first for main content extraction
    try:
        from readability import Document as ReadabilityDoc
        doc = ReadabilityDoc(html)
        html_content = doc.summary()
    except Exception:
        html_content = html

    soup = BeautifulSoup(html_content, 'lxml')

    # Remove noise elements
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    # Extract structured content
    content_blocks = []
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'table', 'pre', 'blockquote']):
        text = element.get_text(separator='\n', strip=True)
        if not text:
            continue

        tag = element.name
        if tag.startswith('h'):
            level = int(tag[1])
            content_blocks.append(f"{'#' * level} {text}")
        elif tag in ('ul', 'ol'):
            content_blocks.append(text)
        elif tag == 'li':
            content_blocks.append(f"- {text}")
        elif tag == 'table':
            table_md = _table_to_md(element)
            if table_md:
                content_blocks.append(table_md)
        else:
            content_blocks.append(text)

    result = '\n\n'.join(content_blocks)
    if result and len(result.strip()) > 100:
        return result
    return None


def _table_to_md(table) -> str:
    """Convert BeautifulSoup table element to Markdown table string."""
    rows = table.find_all('tr')
    if not rows:
        return ""

    md_rows = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if not cells:
            continue
        md_row = '| ' + ' | '.join(cell.get_text(strip=True) for cell in cells) + ' |'
        md_rows.append(md_row)

    if not md_rows:
        return ""

    # Add separator after header row
    col_count = len(rows[0].find_all(['td', 'th']))
    separator = '| ' + ' | '.join(['---'] * col_count) + ' |'
    md_rows.insert(1, separator)

    return '\n'.join(md_rows)


# =====================================================================
#  SPLIT BY HEADINGS → List[Document] (virtual pages)
# =====================================================================

def _split_content(
    markdown: str,
    source: str,
    document_id: str,
    pipeline_version: str,
) -> List[Document]:
    """
    Split Markdown content thành Documents theo headings (virtual pages).
    KHÔNG pre-chunk — để chunk_documents() xử lý parent/child splitting.

    UUIDv5 deterministic với {document_id}_{pipeline_version} → idempotent reindex.
    """
    documents = []

    # Split by headings
    headers_to_split_on = [
        ("#", "Header-1"),
        ("##", "Header-2"),
        ("###", "Header-3"),
        ("####", "Header-4"),
    ]

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )

    try:
        md_splits = md_splitter.split_text(markdown)
        # Convert split results to Document objects
        from langchain_core.documents import Document as LCDoc
        md_docs = [LCDoc(page_content=chunk.page_content, metadata=chunk.metadata) for chunk in md_splits]
    except Exception as exc:
        logger.warning("[HtmlParser] MarkdownHeaderTextSplitter failed: %s. Using raw content.", exc)
        md_docs = [Document(page_content=markdown, metadata={})]

    for chunk_idx, doc in enumerate(md_docs):
        content = doc.page_content.strip()
        if not content:
            continue

        # Sanitize Markdown
        clean_content = MarkdownSanitizer.sanitize(content)
        if not clean_content:
            continue

        # UUIDv5 deterministic: document_id + pipeline_version + chunk_idx
        doc_id = str(uuid.uuid5(
            NAMESPACE_HTML,
            f"{document_id}_{pipeline_version}_{chunk_idx}"
        ))
        documents.append(
            Document(
                page_content=clean_content,
                metadata={
                    "source": source,
                    "page": chunk_idx + 1,
                    "doc_id": doc_id,
                }
            )
        )

    # Fallback: nếu không có document nào được tạo
    if not documents:
        clean_content = MarkdownSanitizer.sanitize(markdown)
        if clean_content:
            doc_id = str(uuid.uuid5(
                NAMESPACE_HTML,
                f"{document_id}_{pipeline_version}_0"
            ))
            documents.append(
                Document(
                    page_content=clean_content,
                    metadata={
                        "source": source,
                        "page": 1,
                        "doc_id": doc_id,
                    }
                )
            )

    logger.info(
        "[HtmlParser] → %d Document objects from %s (document_id=%s)",
        len(documents), source, document_id,
    )
    return documents


# =====================================================================
#  PUBLIC API
# =====================================================================

def parse_html(
    file_path: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    """
    Entry point — Parse HTML → List[Document].

    Args:
        file_path: Absolute path to .html/.htm file.
        document_id: Unique document ID (from upload contract).
        pipeline_version: Pipeline version string (e.g., "v1").

    Returns:
        List[Document] with metadata {source, page, doc_id}.

    Raises:
        ValueError: If file is not valid HTML or has no extractable content.
    """
    _magic_check(file_path)

    source = os.path.basename(file_path)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # Primary: Trafilatura
    try:
        result = _extract_with_trafilatura(html)
        if result:
            logger.info("[HtmlParser] Trafilatura success: %d chars", len(result))
            return _split_content(result, source, document_id, pipeline_version)
    except Exception as exc:
        logger.warning("[HtmlParser] Trafilatura failed: %s. Trying fallback.", exc)

    # Fallback: BeautifulSoup + Readability
    try:
        result = _extract_with_bsoup_fallback(html)
        if result:
            logger.info("[HtmlParser] BSoup fallback success: %d chars", len(result))
            return _split_content(result, source, document_id, pipeline_version)
    except Exception as exc:
        logger.warning("[HtmlParser] BSoup fallback failed: %s", exc)

    # Last resort: raw text extraction
    logger.warning("[HtmlParser] All extraction methods failed. Using raw text.")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    raw_text = soup.get_text(separator='\n\n', strip=True)

    if raw_text and len(raw_text.strip()) > 100:
        return _split_content(raw_text, source, document_id, pipeline_version)

    raise ValueError(f"No extractable content from HTML file: {source}")


# =====================================================================
#  SELF-TEST
# =====================================================================

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage: python html_parser.py <file.html> [document_id] [pipeline_version]")
        sys.exit(1)

    file_path = sys.argv[1]
    doc_id = sys.argv[2] if len(sys.argv) > 2 else "test-document-id"
    pipe_ver = sys.argv[3] if len(sys.argv) > 3 else "v1"

    start = time.time()
    docs = parse_html(file_path, doc_id, pipe_ver)
    elapsed = time.time() - start

    print(f"Parsed: {len(docs)} pages in {elapsed:.2f}s")
    for doc in docs:
        print(f"--- Page {doc.metadata['page']} ({len(doc.page_content)} chars)")
        print(f"    doc_id: {doc.metadata['doc_id']}")
        print(doc.page_content[:300])
