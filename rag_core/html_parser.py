"""
html_parser.py — HTML Parser for RAG pipeline.

Pipeline:
  1. Flexible magic check (BSoup detect <html> tag)
  2. Primary: Readability-lxml extracts clean main-content HTML (removes nav/sidebar/ads)
  3. BSoup converts clean HTML → Markdown (headings #, tables |, code blocks ```)
  4. Reuse _sanitize_and_split from md_parser (heading split + UUIDv5, skip sanitize)
  5. Heading chain preserved in metadata for citation accuracy

Sources:
  - parse_html(file_path)          → đọc file + parse
  - parse_html_bytes(html, ...)     → parse từ string (in-memory)
  - parse_html_from_url(url, ...)   → download URL + parse

=== FRONTEND API GUIDE ===

I. INGEST URL

  POST /api/ingest/url
  Headers: Authorization: Bearer <token>
  Body: { "url": "https://example.com/document.html" }

  Response 202:
  {
    "document_id": "uuid",
    "job_id": "uuid",
    "status": "queued",
    "pipeline_version": "...",
    "url": "https://example.com/document.html"
  }

  Example (fetch):
    const res = await fetch('/api/ingest/url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })
    const { job_id, document_id } = await res.json()

II. POLL JOB STATUS

  GET /api/jobs/{job_id}
  Headers: Authorization: Bearer <token>

  Response when done:
  {
    "job_id": "...",
    "status": "succeeded",        // "succeeded" | "failed" | "running" | "queued"
    "stage": "persisting_metadata",
    "progress_pct": 100,
    "stage_detail": "completed",
    "error_message": null,        // string if failed
    "pipeline_version": "...",
    "queued_at": "2026-05-22T...",
    "started_at": "2026-05-22T...",
    "finished_at": "2026-05-22T..."
  }

  Polling strategy: fetch every 2s until status !== "running" && status !== "queued"

III. GET DOCUMENTS LIST

  GET /api/documents
  Headers: Authorization: Bearer <token>

  Response:
  [{
    "document_id": "uuid",
    "filename": "https://example.com/document.html",
    "object_key": "url://https://...",
    "mime_type": "text/html",
    "size_bytes": 0,
    "created_at": "...",
    "updated_at": "...",
    "latest_job": { ... }  // latest job status (or null)
  }]

IV. CITATION METADATA (for chat UI)

  Mỗi chunk trả về trong streaming response có metadata:
  {
    "source": "https://example.com/document.html",
    "page": 1,
    "doc_id": "uuid-v5",
    "Header-1": "Chương 1",         // optional
    "Header-2": "1.1 Giới thiệu"    // optional
  }

  Hiển thị citation path trong bubble chat:
    "Theo nguồn (Chương 1 > 1.1 Giới thiệu) ... nội dung trích dẫn"

  Cách parse heading chain từ metadata trong JS:
    const headers = Object.entries(chunk.metadata || {})
      .filter(([k]) => k.startsWith('Header-'))
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([, v]) => v)
    // → ["Chương 1", "1.1 Giới thiệu"]
    const citationPath = headers.join(' > ')
"""

from __future__ import annotations

import os
import uuid
from typing import List, Optional

from bs4 import BeautifulSoup
from langchain_core.documents import Document

try:
    from .common.logging_utils import configure_logging, get_logger
    from .md_parser import _sanitize_and_split
except ImportError:  # pragma: no cover
    from common.logging_utils import configure_logging, get_logger
    from md_parser import _sanitize_and_split

configure_logging()
logger = get_logger(__name__)

NAMESPACE_HTML = uuid.uuid5(uuid.NAMESPACE_URL, "html.parser.rag.uet.edu.vn")
MIN_CONTENT_LENGTH = 100

DEFAULT_URL_TIMEOUT = 30
DEFAULT_URL_MAX_BYTES = 10 * 1024 * 1024


# =====================================================================
#  VALIDATION
# =====================================================================

def _validate_html_content(content: bytes) -> None:
    """Validate bytes contain HTML structure."""
    try:
        text = content.decode('utf-8', errors='ignore').lower()
    except Exception:
        raise ValueError("Cannot read file as text")

    if '<html' in text or '<!doctype' in text:
        return

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
#  PRIMARY: READABILITY + BEAUTIFULSOUP (clean HTML → Markdown)
# =====================================================================

def _extract_with_readability(html: str) -> Optional[BeautifulSoup]:
    """
    Extract clean main-content HTML using Mozilla Readability algorithm.
    Returns a BeautifulSoup object of the cleaned HTML, or None if extraction fails.
    """
    try:
        from readability import Document
        doc = Document(html)
        summary = doc.summary()
        if not summary or len(summary.strip()) < MIN_CONTENT_LENGTH:
            return None
        soup = BeautifulSoup(summary, 'lxml')
        for tag in soup(['script', 'style']):
            tag.decompose()
        return soup
    except Exception as exc:
        logger.warning("[HtmlParser] Readability extraction failed: %s", exc)
        return None


def _html_to_markdown(soup: BeautifulSoup) -> str:
    """
    Convert clean HTML (from Readability) to Markdown text suitable for
    MarkdownHeaderTextSplitter. Handles headings, tables, code blocks,
    paragraphs, lists, and blockquotes.

    Traversal rules:
    - Container tags (div, section, article, main, ol, ul): recurse children
    - Leaf block tags (p, li, blockquote): extract text as paragraph
    - Headings (h1-h6): convert to # heading syntax
    - Tables: convert to | pipe-style Markdown
    - Code (pre, code): wrap in ```
    - Other tags: recurse children (unwrap)
    """
    lines: list[str] = []
    CONTAINERS = {'div', 'section', 'article', 'main', 'ol', 'ul', 'nav', 'header', 'footer'}
    LEAF_BLOCKS = {'p', 'li', 'blockquote', 'th', 'td', 'dt', 'dd'}
    HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}

    def process_table(table_el):
        md_lines = []
        rows = table_el.find_all('tr')
        if not rows:
            return
        headers = rows[0].find_all(['th', 'td'])
        header_cells = [h.get_text(' ', strip=True) for h in headers]
        md_lines.append('| ' + ' | '.join(header_cells) + ' |')
        md_lines.append('| ' + ' | '.join(['---'] * len(header_cells)) + ' |')
        for row in rows[1:]:
            cells = row.find_all(['th', 'td'])
            cell_texts = [c.get_text(' ', strip=True) for c in cells]
            md_lines.append('| ' + ' | '.join(cell_texts) + ' |')
        lines.extend(md_lines)
        lines.append('')

    def process_node(el):
        if not hasattr(el, 'name') or not el.name:
            return

        # Headings
        if el.name in HEADINGS:
            level = int(el.name[1])
            text = el.get_text(' ', strip=True)
            if text:
                lines.append('#' * level + ' ' + text)
                lines.append('')
            return

        # Tables
        if el.name == 'table':
            process_table(el)
            return

        # Code blocks
        if el.name in ('pre', 'code'):
            code_text = el.get_text()
            if code_text.strip():
                lines.append('```')
                lines.append(code_text.rstrip())
                lines.append('```')
                lines.append('')
            return

        # Leaf blocks: extract text directly
        if el.name in LEAF_BLOCKS:
            text = el.get_text(' ', strip=True)
            if text:
                prefix = ''
                if el.name == 'li':
                    parent = el.parent
                    if parent and parent.name == 'ol':
                        idx = list(parent.children).index(el) + 1
                        prefix = '%d. ' % idx
                    else:
                        prefix = '- '
                elif el.name == 'blockquote':
                    prefix = '> '
                lines.append(prefix + text)
                lines.append('')
            return

        # Container / unknown: recurse children
        if el.name in CONTAINERS or True:
            for child in el.children:
                process_node(child)

    process_node(soup.body or soup)
    result = '\n'.join(lines).strip()
    return result


# =====================================================================
#  LAST RESORT: BSoup raw text (when Readability fails)
# =====================================================================

def _extract_raw_text(html: str) -> Optional[str]:
    """
    Last-resort extraction: BSoup raw text with noise removal.
    Used when Readability fails to produce meaningful output.
    """
    try:
        try:
            soup = BeautifulSoup(html, 'lxml')
        except Exception:
            soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        raw_text = soup.get_text(separator='\n\n', strip=True)
        if raw_text and len(raw_text) > MIN_CONTENT_LENGTH:
            return raw_text
    except Exception as exc:
        logger.warning("[HtmlParser] Raw text extraction failed: %s", exc)
    return None


# =====================================================================
#  CORE: parse HTML string → List[Document]  (in-memory, no I/O)
# =====================================================================

def parse_html_bytes(
    html: str,
    source: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    """
    Core: Parse HTML string → List[Document].

    Pipeline:
      1. Readability-lxml extracts clean main-content HTML (removes nav/sidebar/ads).
      2. BSoup converts clean HTML to Markdown (headings, tables, code blocks).
      3. _sanitize_and_split splits by Markdown headings → List[Document].
         (skip_sanitize=True since Readability output is already clean.)

    Args:
        html: Raw HTML content as string.
        source: Identifier (filename, URL) — stored in metadata.
        document_id: Unique document ID (from upload contract).
        pipeline_version: Pipeline version string.

    Returns:
        List[Document] with metadata {source, page, doc_id, headings...}.

    Raises:
        ValueError: If no extractable content.
    """
    # Primary: Readability + BSoup → Markdown
    try:
        soup = _extract_with_readability(html)
        if soup is not None:
            markdown = _html_to_markdown(soup)
            if markdown and len(markdown) > MIN_CONTENT_LENGTH:
                logger.info(
                    "[HtmlParser] Readability success: %d chars → %d chars Markdown",
                    len(str(soup)), len(markdown),
                )
                return _sanitize_and_split(
                    markdown, source, document_id, pipeline_version,
                    namespace=NAMESPACE_HTML, skip_sanitize=True,
                )
    except Exception as exc:
        logger.warning("[HtmlParser] Readability pipeline failed: %s", exc)

    # Last resort: BSoup raw text extraction
    raw_text = _extract_raw_text(html)
    if raw_text:
        logger.info("[HtmlParser] Raw text fallback success: %d chars", len(raw_text))
        return _sanitize_and_split(
            raw_text, source, document_id, pipeline_version,
            namespace=NAMESPACE_HTML, skip_sanitize=True,
        )

    raise ValueError(f"No extractable content from HTML source: {source}")


# =====================================================================
#  SOURCE: FILE
# =====================================================================

def parse_html(
    file_path: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    """
    Entry point — Parse .html/.htm file → List[Document].

    Args:
        file_path: Absolute path to .html/.htm file.
        document_id: Unique document ID (from upload contract).
        pipeline_version: Pipeline version string.

    Returns:
        List[Document] with metadata {source, page, doc_id, headings...}.

    Raises:
        ValueError: If file is not valid HTML or has no extractable content.
    """
    with open(file_path, 'rb') as f:
        content = f.read()
    _validate_html_content(content[:8192])
    source = os.path.basename(file_path)
    html = content.decode('utf-8', errors='ignore').lstrip('\ufeff')

    return parse_html_bytes(html, source, document_id, pipeline_version)


# =====================================================================
#  SOURCE: URL
# =====================================================================

def parse_html_from_url(
    url: str,
    document_id: str,
    pipeline_version: str = "v1",
    timeout: int = DEFAULT_URL_TIMEOUT,
    max_bytes: int = DEFAULT_URL_MAX_BYTES,
) -> List[Document]:
    """
    Download URL → Parse HTML content → List[Document].

    Args:
        url: Full URL to fetch (http/https).
        document_id: Unique document ID.
        pipeline_version: Pipeline version string.
        timeout: Request timeout in seconds.
        max_bytes: Maximum response size.

    Returns:
        List[Document] with metadata {source, page, doc_id, headings...}.

    Raises:
        ValueError: If URL is invalid, not HTML, or has no extractable content.
        urllib.error.URLError: If network error or timeout.
    """
    import urllib.request

    logger.info("[HtmlParser] Fetching URL: %s", url)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; RAG-Philosophy/1.0; +https://uet.vnu.edu.vn)",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            logger.warning(
                "[HtmlParser] Unexpected Content-Type: %s — proceeding anyway", content_type,
            )

        content = resp.read()
        if len(content) > max_bytes:
            raise ValueError(
                f"URL content too large ({len(content)} bytes > {max_bytes})"
            )

    _validate_html_content(content[:8192])
    source = url
    html = content.decode('utf-8', errors='ignore').lstrip('\ufeff')

    return parse_html_bytes(html, source, document_id, pipeline_version)


# =====================================================================
#  SELF-TEST
# =====================================================================

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python html_parser.py <file.html> [document_id] [pipeline_version]")
        print("  python html_parser.py --url <url> [document_id] [pipeline_version]")
        sys.exit(1)

    doc_id = "test-document-id"
    pipe_ver = "v1"

    start = time.time()

    if sys.argv[1] == "--url" and len(sys.argv) >= 3:
        url = sys.argv[2]
        doc_id = sys.argv[3] if len(sys.argv) > 3 else doc_id
        pipe_ver = sys.argv[4] if len(sys.argv) > 4 else pipe_ver
        docs = parse_html_from_url(url, doc_id, pipe_ver)
    else:
        file_path = sys.argv[1]
        doc_id = sys.argv[2] if len(sys.argv) > 2 else doc_id
        pipe_ver = sys.argv[3] if len(sys.argv) > 3 else pipe_ver
        docs = parse_html(file_path, doc_id, pipe_ver)

    elapsed = time.time() - start
    print(f"Parsed: {len(docs)} pages in {elapsed:.2f}s")
    for doc in docs:
        print(f"--- Page {doc.metadata['page']} ({len(doc.page_content)} chars)")
        print(f"    doc_id: {doc.metadata['doc_id']}")
        headings = {k: v for k, v in doc.metadata.items() if k.startswith("Header-")}
        print(f"    headings: {headings}")
        print(doc.page_content[:300])
