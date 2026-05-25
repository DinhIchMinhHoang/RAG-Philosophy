from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class RenderError(RuntimeError):
    pass


def _split_priority(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    items = [part.strip().lower() for part in value.split(",")]
    cleaned = [item for item in items if item]
    return cleaned or default


def _run(command: list[str], timeout_seconds: int) -> None:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        message = stderr or stdout or f"exit_code={completed.returncode}"
        raise RenderError(message)


def _pick_executable(candidates: list[str]) -> str | None:
    for name in candidates:
        resolved = shutil.which(name)
        if resolved:
            return resolved
    return None


def _expect_file(path: Path, renderer: str) -> None:
    if not path.exists() or path.stat().st_size <= 0:
        raise RenderError(f"{renderer} did not produce a PDF file: {path}")


def render_docx_to_pdf(
    docx_path: str,
    *,
    timeout_seconds: int,
    priority: list[str],
) -> str:
    src = Path(docx_path)
    if not src.exists():
        raise RenderError(f"DOCX not found: {docx_path}")

    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="docx_render_") as tmpdir:
        outdir = Path(tmpdir)
        out_pdf = outdir / f"{src.stem}.pdf"

        for renderer in priority:
            try:
                if renderer == "soffice":
                    executable = _pick_executable(["soffice", "libreoffice"])
                    if not executable:
                        raise RenderError("soffice/libreoffice not found")
                    _run(
                        [
                            executable,
                            "--headless",
                            "--convert-to",
                            "pdf",
                            "--outdir",
                            str(outdir),
                            str(src),
                        ],
                        timeout_seconds,
                    )
                    _expect_file(out_pdf, renderer)
                elif renderer == "pandoc":
                    executable = _pick_executable(["pandoc"])
                    if not executable:
                        raise RenderError("pandoc not found")
                    _run(
                        [executable, str(src), "-o", str(out_pdf)],
                        timeout_seconds,
                    )
                    _expect_file(out_pdf, renderer)
                else:
                    raise RenderError(f"unsupported DOCX renderer: {renderer}")

                final_fd, final_tmp = tempfile.mkstemp(prefix="docx_ocr_", suffix=".pdf")
                os.close(final_fd)
                final_pdf = Path(final_tmp)
                out_pdf.replace(final_pdf)
                return str(final_pdf)
            except Exception as exc:
                errors.append(f"{renderer}: {exc}")

    raise RenderError("All DOCX renderers failed: " + " | ".join(errors))


def render_html_to_pdf_path(
    html_path: str,
    *,
    timeout_seconds: int,
    priority: list[str],
) -> str:
    src = Path(html_path)
    if not src.exists():
        raise RenderError(f"HTML not found: {html_path}")

    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="html_render_") as tmpdir:
        outdir = Path(tmpdir)
        out_pdf = outdir / f"{src.stem}.pdf"
        file_url = src.resolve().as_uri()

        for renderer in priority:
            try:
                if renderer == "chrome":
                    executable = _pick_executable(
                        ["chrome", "chromium", "msedge", "google-chrome"]
                    )
                    if not executable:
                        raise RenderError("chrome/chromium/msedge not found")
                    _run(
                        [
                            executable,
                            "--headless",
                            "--disable-gpu",
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--no-first-run",
                            "--no-default-browser-check",
                            f"--print-to-pdf={out_pdf}",
                            file_url,
                        ],
                        timeout_seconds,
                    )
                    _expect_file(out_pdf, renderer)
                elif renderer == "wkhtmltopdf":
                    executable = _pick_executable(["wkhtmltopdf"])
                    if not executable:
                        raise RenderError("wkhtmltopdf not found")
                    _run(
                        [executable, str(src), str(out_pdf)],
                        timeout_seconds,
                    )
                    _expect_file(out_pdf, renderer)
                else:
                    raise RenderError(f"unsupported HTML renderer: {renderer}")

                final_fd, final_tmp = tempfile.mkstemp(prefix="html_ocr_", suffix=".pdf")
                os.close(final_fd)
                final_pdf = Path(final_tmp)
                out_pdf.replace(final_pdf)
                return str(final_pdf)
            except Exception as exc:
                errors.append(f"{renderer}: {exc}")

    raise RenderError("All HTML renderers failed: " + " | ".join(errors))


def render_html_to_pdf_html(
    html_text: str,
    *,
    timeout_seconds: int,
    priority: list[str],
) -> str:
    fd, html_tmp = tempfile.mkstemp(prefix="html_ocr_", suffix=".html")
    os.close(fd)
    html_path = Path(html_tmp)
    try:
        html_path.write_text(html_text, encoding="utf-8")
        return render_html_to_pdf_path(
            str(html_path),
            timeout_seconds=timeout_seconds,
            priority=priority,
        )
    finally:
        html_path.unlink(missing_ok=True)
