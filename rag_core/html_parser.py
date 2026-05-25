"""
HTML parser for the RAG pipeline.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup
from langchain_core.documents import Document

try:
    from .common.logging_utils import configure_logging, get_logger
    from .common.nonpdf_renderers import _split_priority, render_html_to_pdf_html
    from .config import Config
    from .md_parser import _sanitize_and_split
    from .step1_parser import HybridPDFParser
except ImportError:  # pragma: no cover
    from common.logging_utils import configure_logging, get_logger
    from common.nonpdf_renderers import _split_priority, render_html_to_pdf_html
    from config import Config
    from md_parser import _sanitize_and_split
    from step1_parser import HybridPDFParser

configure_logging()
logger = get_logger(__name__)

NAMESPACE_HTML = uuid.uuid5(uuid.NAMESPACE_URL, "html.parser.rag.uet.edu.vn")
MIN_CONTENT_LENGTH = 100

DEFAULT_URL_TIMEOUT = 30
DEFAULT_URL_MAX_BYTES = 10 * 1024 * 1024


def _nonpdf_mode() -> str:
    mode = (Config.OCR_NONPDF_MODE or "primary").strip().lower()
    if mode not in {"primary", "strict", "assist"}:
        return "primary"
    return mode


def _validate_html_content(content: bytes) -> None:
    try:
        text = content.decode("utf-8", errors="ignore").lower()
    except Exception as exc:
        raise ValueError("Cannot read file as text") from exc

    if "<html" in text or "<!doctype" in text:
        return

    soup = BeautifulSoup(content, "html.parser")
    if not soup.find(["html", "head", "body"]):
        raise ValueError(
            "Unsupported file format. Expected .html/.htm, "
            "but file signature does not match."
        )


def _extract_with_readability(html: str) -> Optional[BeautifulSoup]:
    try:
        from readability import Document as ReadabilityDocument

        doc = ReadabilityDocument(html)
        summary = doc.summary()
        if not summary or len(summary.strip()) < MIN_CONTENT_LENGTH:
            return None
        soup = BeautifulSoup(summary, "lxml")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup
    except Exception as exc:
        logger.warning("[HtmlParser] Readability extraction failed: %s", exc)
        return None


def _html_to_markdown(soup: BeautifulSoup) -> str:
    lines: list[str] = []
    containers = {"div", "section", "article", "main", "ol", "ul", "nav", "header", "footer"}
    leaf_blocks = {"p", "li", "blockquote", "th", "td", "dt", "dd"}
    headings = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def process_table(table_el: BeautifulSoup) -> None:
        rows = table_el.find_all("tr")
        if not rows:
            return
        header_cells = [h.get_text(" ", strip=True) for h in rows[0].find_all(["th", "td"])]
        lines.append("| " + " | ".join(header_cells) + " |")
        lines.append("| " + " | ".join(["---"] * len(header_cells)) + " |")
        for row in rows[1:]:
            cell_texts = [c.get_text(" ", strip=True) for c in row.find_all(["th", "td"])]
            lines.append("| " + " | ".join(cell_texts) + " |")
        lines.append("")

    def process_node(el: BeautifulSoup) -> None:
        if not getattr(el, "name", None):
            return
        if el.name in headings:
            text = el.get_text(" ", strip=True)
            if text:
                level = int(el.name[1])
                lines.append("#" * level + " " + text)
                lines.append("")
            return
        if el.name == "table":
            process_table(el)
            return
        if el.name in {"pre", "code"}:
            code = el.get_text()
            if code.strip():
                lines.append("```")
                lines.append(code.rstrip())
                lines.append("```")
                lines.append("")
            return
        if el.name in leaf_blocks:
            text = el.get_text(" ", strip=True)
            if text:
                prefix = ""
                if el.name == "li":
                    parent = el.parent
                    if parent and getattr(parent, "name", None) == "ol":
                        prefix = f"{list(parent.children).index(el) + 1}. "
                    else:
                        prefix = "- "
                elif el.name == "blockquote":
                    prefix = "> "
                lines.append(prefix + text)
                lines.append("")
            return
        if el.name in containers or True:
            for child in el.children:
                process_node(child)

    process_node(soup.body or soup)
    return "\n".join(lines).strip()


def _extract_raw_text(html: str) -> Optional[str]:
    try:
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        raw = soup.get_text(separator="\n\n", strip=True)
        if raw and len(raw) > MIN_CONTENT_LENGTH:
            return raw
    except Exception as exc:
        logger.warning("[HtmlParser] Raw text extraction failed: %s", exc)
    return None


def _clean_html_for_ocr(html: str) -> str:
    soup = _extract_with_readability(html)
    if soup is not None:
        return str(soup)
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return str(soup)


def _parse_html_via_ocr(
    html: str,
    source: str,
    document_id: str,
    pipeline_version: str,
) -> List[Document]:
    cleaned_html = _clean_html_for_ocr(html)
    rendered_pdf = render_html_to_pdf_html(
        cleaned_html,
        timeout_seconds=Config.OCR_RENDER_TIMEOUT_SECONDS,
        priority=_split_priority(
            Config.OCR_RENDERER_HTML_PRIORITY,
            default=["chrome", "wkhtmltopdf"],
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
        raise ValueError("OCR produced empty markdown for HTML")

    logger.info("[HtmlParser] OCR path success: %d chars", len(markdown))
    return _sanitize_and_split(
        markdown,
        source,
        document_id,
        pipeline_version,
        namespace=NAMESPACE_HTML,
    )


def parse_html_bytes(
    html: str,
    source: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    mode = _nonpdf_mode()
    if Config.OCR_HTML_ENABLED and mode in {"primary", "strict"}:
        try:
            return _parse_html_via_ocr(html, source, document_id, pipeline_version)
        except Exception as exc:
            if mode == "strict":
                raise ValueError(f"HTML OCR strict mode failed: {exc}") from exc
            logger.warning("[HtmlParser] OCR path failed, fallback to text parser: %s", exc)

    try:
        soup = _extract_with_readability(html)
        if soup is not None:
            markdown = _html_to_markdown(soup)
            if markdown and len(markdown) > MIN_CONTENT_LENGTH:
                logger.info(
                    "[HtmlParser] Readability success: %d chars -> %d chars Markdown",
                    len(str(soup)),
                    len(markdown),
                )
                return _sanitize_and_split(
                    markdown,
                    source,
                    document_id,
                    pipeline_version,
                    namespace=NAMESPACE_HTML,
                    skip_sanitize=True,
                )
    except Exception as exc:
        logger.warning("[HtmlParser] Readability pipeline failed: %s", exc)

    try:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        markdown = _html_to_markdown(soup)
        if markdown:
            logger.info("[HtmlParser] BeautifulSoup Markdown fallback success: %d chars", len(markdown))
            return _sanitize_and_split(
                markdown,
                source,
                document_id,
                pipeline_version,
                namespace=NAMESPACE_HTML,
                skip_sanitize=True,
            )
    except Exception as exc:
        logger.warning("[HtmlParser] BeautifulSoup Markdown fallback failed: %s", exc)

    raw_text = _extract_raw_text(html)
    if raw_text:
        logger.info("[HtmlParser] Raw text fallback success: %d chars", len(raw_text))
        return _sanitize_and_split(
            raw_text,
            source,
            document_id,
            pipeline_version,
            namespace=NAMESPACE_HTML,
            skip_sanitize=True,
        )

    raise ValueError(f"No extractable content from HTML source: {source}")


def parse_html(
    file_path: str,
    document_id: str,
    pipeline_version: str = "v1",
) -> List[Document]:
    with open(file_path, "rb") as f:
        content = f.read()
    _validate_html_content(content[:8192])
    source = os.path.basename(file_path)
    html = content.decode("utf-8", errors="ignore").lstrip("\ufeff")
    return parse_html_bytes(html, source, document_id, pipeline_version)


def parse_html_from_url(
    url: str,
    document_id: str,
    pipeline_version: str = "v1",
    timeout: int = DEFAULT_URL_TIMEOUT,
    max_bytes: int = DEFAULT_URL_MAX_BYTES,
) -> List[Document]:
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
            logger.warning("[HtmlParser] Unexpected Content-Type: %s - proceeding anyway", content_type)

        content = resp.read()
        if len(content) > max_bytes:
            raise ValueError(f"URL content too large ({len(content)} bytes > {max_bytes})")

    _validate_html_content(content[:8192])
    html = content.decode("utf-8", errors="ignore").lstrip("\ufeff")
    return parse_html_bytes(html, url, document_id, pipeline_version)


if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python html_parser.py <file.html> [document_id] [pipeline_version]")
        print("  python html_parser.py --url <url> [document_id] [pipeline_version]")
        raise SystemExit(1)

    start = time.time()
    if sys.argv[1] == "--url":
        if len(sys.argv) < 3:
            raise SystemExit("Missing URL")
        target = sys.argv[2]
        doc_id = sys.argv[3] if len(sys.argv) > 3 else "test-document-id"
        pipe_ver = sys.argv[4] if len(sys.argv) > 4 else "v1"
        docs = parse_html_from_url(target, doc_id, pipe_ver)
    else:
        target = sys.argv[1]
        doc_id = sys.argv[2] if len(sys.argv) > 2 else "test-document-id"
        pipe_ver = sys.argv[3] if len(sys.argv) > 3 else "v1"
        docs = parse_html(target, doc_id, pipe_ver)

    elapsed = time.time() - start
    print(f"Parsed: {len(docs)} pages in {elapsed:.2f}s")
    for doc in docs[:3]:
        print(f"--- Page {doc.metadata.get('page')} ({len(doc.page_content)} chars)")
        print(doc.page_content[:200])
