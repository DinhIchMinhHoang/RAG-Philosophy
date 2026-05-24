from __future__ import annotations

import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from sqlalchemy.orm import Session

from rag_core.common.embeddings import get_embeddings
from rag_core.step1_parser import HybridPDFParser
from rag_core.step2_chunker import chunk_documents

from ..models import DocumentChunk, DocumentRecord
from .idempotency import delete_chunks_for_document_version
from .job_updater import JobUpdater
from .logging_utils import log_event
from .qdrant_store import (
    build_qdrant_client,
    delete_vectors_for_document_version,
    upsert_child_vectors,
)
from .storage import storage_client, validate_file_bytes


@dataclass
class ChunkDraft:
    id: str
    document_id: str
    owner_id: int | None
    notebook_id: int | None
    job_id: str
    kind: str
    parent_chunk_id: str | None
    chunk_order: int
    text: str
    source: str
    page: int
    doc_id: str
    pipeline_version: str


def _strip_nul_chars(value: str) -> str:
    return value.replace("\x00", "")


def _clean_required_metadata(doc: Document, key: str) -> str:
    value = _strip_nul_chars(str(doc.metadata[key]))
    if not value:
        raise ValueError(f"Document metadata field is empty after sanitization: {key}")
    return value


def _clean_page_content(doc: Document) -> str:
    return _strip_nul_chars(doc.page_content or "")



def _draft_to_model(draft: ChunkDraft) -> DocumentChunk:
    return DocumentChunk(
        id=draft.id,
        document_id=draft.document_id,
        owner_id=draft.owner_id,
        notebook_id=draft.notebook_id,
        job_id=draft.job_id,
        kind=draft.kind,
        parent_chunk_id=draft.parent_chunk_id,
        chunk_order=draft.chunk_order,
        text=draft.text,
        source=draft.source,
        page=draft.page,
        doc_id=draft.doc_id,
        pipeline_version=draft.pipeline_version,
    )


def _normalize_parsed_page_sources(parsed_pages: list[Document], filename: str) -> None:
    for page in parsed_pages:
        page.metadata["source"] = filename



def _build_chunk_drafts(
    document_id: str,
    owner_id: int | None,
    notebook_id: int | None,
    job_id: str,
    pipeline_version: str,
    parent_docs: list[Document],
    child_docs: list[Document],
) -> tuple[list[ChunkDraft], list[ChunkDraft]]:
    parent_drafts: list[ChunkDraft] = []
    parent_by_doc_id: dict[str, str] = {}

    for idx, parent_doc in enumerate(parent_docs):
        parent_id = str(uuid.uuid4())
        doc_id = _clean_required_metadata(parent_doc, "doc_id")
        parent_by_doc_id[doc_id] = parent_id
        parent_drafts.append(
            ChunkDraft(
                id=parent_id,
                document_id=document_id,
                owner_id=owner_id,
                notebook_id=notebook_id,
                job_id=job_id,
                kind="parent",
                parent_chunk_id=None,
                chunk_order=idx,
                text=_clean_page_content(parent_doc),
                source=_clean_required_metadata(parent_doc, "source"),
                page=int(parent_doc.metadata["page"]),
                doc_id=doc_id,
                pipeline_version=pipeline_version,
            )
        )

    child_drafts: list[ChunkDraft] = []
    for idx, child_doc in enumerate(child_docs):
        doc_id = _clean_required_metadata(child_doc, "doc_id")
        parent_chunk_id = parent_by_doc_id.get(doc_id)
        if not parent_chunk_id:
            raise ValueError(f"Child missing parent mapping for doc_id={doc_id}")

        child_drafts.append(
            ChunkDraft(
                id=str(uuid.uuid4()),
                document_id=document_id,
                owner_id=owner_id,
                notebook_id=notebook_id,
                job_id=job_id,
                kind="child",
                parent_chunk_id=parent_chunk_id,
                chunk_order=idx,
                text=_clean_page_content(child_doc),
                source=_clean_required_metadata(child_doc, "source"),
                page=int(child_doc.metadata["page"]),
                doc_id=doc_id,
                pipeline_version=pipeline_version,
            )
        )

    return parent_drafts, child_drafts


def _run_pdf_parse(tmp_path: str) -> list[Document]:
    parser = HybridPDFParser()
    return parser.parse_pdf(tmp_path)


def _run_docx_parse(
    tmp_path: str,
    document_id: str,
    pipeline_version: str,
) -> list[Document]:
    from rag_core.docx_parser import parse_docx
    return parse_docx(tmp_path, document_id, pipeline_version)


def _run_html_parse(
    tmp_path: str,
    document_id: str,
    pipeline_version: str,
) -> list[Document]:
    from rag_core.html_parser import parse_html
    return parse_html(tmp_path, document_id, pipeline_version)


def _run_md_parse(
    tmp_path: str,
    document_id: str,
    pipeline_version: str,
) -> list[Document]:
    from rag_core.md_parser import parse_md
    return parse_md(tmp_path, document_id, pipeline_version)


def _process_parsed_documents(
    db: Session,
    *,
    job_id: str,
    document_id: str,
    pipeline_version: str,
    parsed_pages: list[Document],
    updater: JobUpdater,
    total_started: float,
) -> dict[str, int]:
    updater = JobUpdater(db)
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if document is None:
        raise ValueError(f"Document not found: {document_id}")

    total_started = time.perf_counter()

    def _mark_stage(stage: str, ratio: float, detail: str) -> None:
        updater.advance_stage(job_id, stage, ratio=ratio, stage_detail=detail)

    updater.start_run(job_id, pipeline_version=pipeline_version)

    # Normalize source metadata (override temp filename → original filename)
    _normalize_parsed_page_sources(parsed_pages, document.filename)

    stage_started = time.perf_counter()
    _mark_stage("chunking", 0.1, "chunking_started")
    child_docs, parent_docs = chunk_documents(parsed_pages)
    if not child_docs or not parent_docs:
        raise ValueError("Chunking produced empty parent/child docs")

    parent_drafts, child_drafts = _build_chunk_drafts(
        document_id=document_id,
        owner_id=document.owner_id,
        notebook_id=document.notebook_id,
        job_id=job_id,
        pipeline_version=pipeline_version,
        parent_docs=parent_docs,
        child_docs=child_docs,
    )

    _mark_stage(
        "chunking",
        1.0,
        f"parents={len(parent_drafts)} children={len(child_drafts)}",
    )
    chunk_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    log_event(
        "info",
        "stage_complete",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="chunking",
        duration_ms=chunk_duration_ms,
    )

    stage_started = time.perf_counter()
    _mark_stage("embedding", 0.05, "embedding_started")
    embedder = get_embeddings()
    child_texts = [draft.text for draft in child_drafts]
    vectors = embedder.embed_documents(child_texts)
    _mark_stage("embedding", 1.0, f"embedded_children={len(child_drafts)}")
    embedding_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    log_event(
        "info",
        "stage_complete",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="embedding",
        duration_ms=embedding_duration_ms,
    )

    stage_started = time.perf_counter()
    _mark_stage("indexing_vector", 0.05, "indexing_started")
    qdrant_client = build_qdrant_client()
    delete_vectors_for_document_version(qdrant_client, document_id, pipeline_version)
    child_chunk_models = [_draft_to_model(draft) for draft in child_drafts]
    upsert_child_vectors(qdrant_client, child_chunk_models, vectors)
    _mark_stage("indexing_vector", 1.0, f"indexed_children={len(child_drafts)}")
    indexing_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    log_event(
        "info",
        "stage_complete",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="indexing_vector",
        duration_ms=indexing_duration_ms,
    )

    stage_started = time.perf_counter()
    _mark_stage("persisting_metadata", 0.05, "metadata_started")
    deleted_chunks = delete_chunks_for_document_version(db, document_id, pipeline_version)
    all_rows = [_draft_to_model(draft) for draft in parent_drafts + child_drafts]
    db.add_all(all_rows)
    db.commit()
    _mark_stage(
        "persisting_metadata",
        1.0,
        f"deleted_old_chunks={deleted_chunks} inserted={len(all_rows)}",
    )
    metadata_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    total_duration_ms = int((time.perf_counter() - total_started) * 1000)
    log_event(
        "info",
        "job_succeeded",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="persisting_metadata",
        duration_ms=total_duration_ms,
    )

    updater.set_state(
        job_id,
        status="succeeded",
        progress_pct=100,
        stage="persisting_metadata",
        stage_detail="completed",
    )

    return {
        "pages": len(parsed_pages),
        "parent_chunks": len(parent_drafts),
        "child_chunks": len(child_drafts),
        "deleted_chunks": deleted_chunks,
        "embedding_duration_ms": embedding_duration_ms,
        "indexing_duration_ms": indexing_duration_ms,
        "metadata_duration_ms": metadata_duration_ms,
    }


def run_ingest_job(
    db: Session,
    *,
    job_id: str,
    document_id: str,
    object_key: str,
    pipeline_version: str,
    user_id: str = "system",
) -> dict[str, int]:
    updater = JobUpdater(db)
    total_started = time.perf_counter()

    def _mark_stage(stage: str, ratio: float, detail: str) -> None:
        updater.advance_stage(job_id, stage, ratio=ratio, stage_detail=detail)

    updater.start_run(job_id, pipeline_version=pipeline_version)

    stage_started = time.perf_counter()
    _mark_stage("fetching_object", 0.1, "fetch_started")
    file_bytes = storage_client.get_bytes(object_key)
    file_ext = validate_file_bytes(object_key, file_bytes)
    _mark_stage("fetching_object", 1.0, f"fetched_bytes={len(file_bytes)}, format={file_ext}")
    fetch_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    log_event(
        "info",
        "stage_complete",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="fetching_object",
        duration_ms=fetch_duration_ms,
    )

    stage_started = time.perf_counter()
    parsed_pages: list[Document] | None = None
    is_excel = False
    excel_result: dict | None = None

    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if file_ext == '.pdf':
            _mark_stage("parsing", 0.1, "parse_started")
            parsed_pages = _run_pdf_parse(tmp_path)

        elif file_ext == '.docx':
            _mark_stage("parsing", 0.1, "parse_started")
            parsed_pages = _run_docx_parse(tmp_path, document_id, pipeline_version)

        elif file_ext in ('.html', '.htm'):
            _mark_stage("parsing", 0.1, "parse_started")
            parsed_pages = _run_html_parse(tmp_path, document_id, pipeline_version)

        elif file_ext == '.md':
            _mark_stage("parsing", 0.1, "parse_started")
            parsed_pages = _run_md_parse(tmp_path, document_id, pipeline_version)

        elif file_ext in ['.xlsx', '.xls', '.csv']:
            is_excel = True
            _mark_stage("loading_sql", 0.1, "excel_ingest_started")
            from .excel_ingestor import ingest_excel_to_sql
            table_records = ingest_excel_to_sql(
                db=db,
                file_bytes=file_bytes,
                file_ext=file_ext,
                document_id=document_id,
                job_id=job_id,
                user_id=user_id,
            )
            _mark_stage("loading_sql", 1.0, f"tables={len(table_records)}")
            sql_duration_ms = int((time.perf_counter() - stage_started) * 1000)
            total_duration_ms = int((time.perf_counter() - total_started) * 1000)
            log_event(
                "info",
                "job_succeeded",
                job_id=job_id,
                document_id=document_id,
                pipeline_version=pipeline_version,
                stage="loading_sql",
                duration_ms=total_duration_ms,
            )
            updater.set_state(
                job_id,
                status="succeeded",
                progress_pct=100,
                stage="loading_sql",
                stage_detail="completed",
            )
            excel_result = {
                "tables": len(table_records),
                "rows": sum(t.row_count for t in table_records),
                "sql_duration_ms": sql_duration_ms,
            }

        else:
            raise ValueError(f"Unsupported format: {file_ext}")

    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)

    if is_excel:
        return excel_result

    if not parsed_pages:
        raise ValueError(f"No pages parsed from {file_ext} file")

    _mark_stage("parsing", 1.0, f"parsed_pages={len(parsed_pages)}")
    parse_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    log_event(
        "info",
        "stage_complete",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="parsing",
        duration_ms=parse_duration_ms,
    )

    return _process_parsed_documents(
        db,
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        parsed_pages=parsed_pages,
        updater=updater,
        total_started=total_started,
    )


def run_url_ingest_job(
    db: Session,
    *,
    job_id: str,
    document_id: str,
    url: str,
    pipeline_version: str,
    user_id: str = "system",
) -> dict[str, int]:
    updater = JobUpdater(db)
    total_started = time.perf_counter()

    def _mark_stage(stage: str, ratio: float, detail: str) -> None:
        updater.advance_stage(job_id, stage, ratio=ratio, stage_detail=detail)

    updater.start_run(job_id, pipeline_version=pipeline_version)

    stage_started = time.perf_counter()
    _mark_stage("fetching_object", 0.1, "url_fetch_started")
    from rag_core.html_parser import parse_html_from_url

    parsed_pages = parse_html_from_url(url, document_id, pipeline_version)
    _mark_stage("fetching_object", 1.0, f"fetched_and_parsed_pages={len(parsed_pages)}")
    fetch_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    log_event(
        "info",
        "stage_complete",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="fetching_object",
        duration_ms=fetch_duration_ms,
    )

    if not parsed_pages:
        raise ValueError(f"No pages parsed from URL: {url}")

    stage_started = time.perf_counter()
    _mark_stage("parsing", 1.0, f"parsed_pages={len(parsed_pages)}")
    parse_duration_ms = int((time.perf_counter() - stage_started) * 1000)
    log_event(
        "info",
        "stage_complete",
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        stage="parsing",
        duration_ms=parse_duration_ms,
    )

    return _process_parsed_documents(
        db,
        job_id=job_id,
        document_id=document_id,
        pipeline_version=pipeline_version,
        parsed_pages=parsed_pages,
        updater=updater,
        total_started=total_started,
    )
