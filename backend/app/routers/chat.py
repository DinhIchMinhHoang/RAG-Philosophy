from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DocumentRecord, IngestJob, Notebook, User
from ..core.dependencies import get_current_user
from ..core.logging_utils import log_api_event
from ..core.settings import settings
from ..services.chat_history import (
    RecentChatMessage,
    get_or_create_conversation,
    load_recent_history,
    save_chat_message,
)
from ..services.chat_runtime import RetrievedContext, chat_runtime_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

EMPTY_NOTEBOOK_ANSWER = (
    "This notebook does not have any processed documents yet. "
    "Please upload a file first so I can answer based on its contents."
)
CHAT_ERROR_ANSWER = (
    "I could not process this chat request right now. "
    "Please try again after the system finishes processing your documents."
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    notebook_id: int | None = None
    selected_source_ids: list[str] | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[dict]
    conversation_id: str
    message_id: str
    rewritten_query: str


@dataclass(frozen=True)
class ChatTurn:
    conversation_id: str
    message: str
    recent_history: list[dict[str, str]]
    rewritten_query: str
    contexts: list[RetrievedContext]
    available_citations: list[dict]


@dataclass
class ChatTiming:
    history_load_ms: int | None = None
    rewrite_ms: int | None = None
    retrieval_ms: int | None = None
    llm_first_token_ms: int | None = None
    total_stream_ms: int | None = None
    error_stage: str | None = None


def _validate_message(message: str) -> str:
    if not message or not message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    return message.strip()


def _history_payload(recent_history: list[RecentChatMessage]) -> list[dict[str, str]]:
    return [{"role": item.role, "content": item.content} for item in recent_history]


def _elapsed_ms(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def _has_ready_notebook_documents(db: Session, *, user_id: int, notebook_id: int) -> bool:
    nb = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    filters = [DocumentRecord.notebook_id == notebook_id, IngestJob.status == "succeeded"]
    if not nb or not nb.is_community:
        filters.append(DocumentRecord.owner_id == user_id)
    return (
        db.query(DocumentRecord.id)
        .join(IngestJob, IngestJob.document_id == DocumentRecord.id)
        .filter(*filters)
        .first()
        is not None
    )


def _normalize_selected_source_ids(selected_source_ids: list[str] | None) -> list[str]:
    if not selected_source_ids:
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for source_id in selected_source_ids:
        value = source_id.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _resolve_selected_source_ids(db: Session, request: ChatRequest, current_user: User) -> list[str]:
    normalized = _normalize_selected_source_ids(request.selected_source_ids)
    if not normalized:
        return []

    owner_filter = DocumentRecord.owner_id == current_user.id
    if request.notebook_id is not None:
        nb = db.query(Notebook).filter(Notebook.id == request.notebook_id).first()
        if nb and nb.is_community:
            owner_filter = DocumentRecord.notebook_id == request.notebook_id

    owned_query = db.query(DocumentRecord.id).filter(
        owner_filter,
        DocumentRecord.id.in_(normalized),
    )
    if request.notebook_id is not None:
        owned_query = owned_query.filter(DocumentRecord.notebook_id == request.notebook_id)

    found_ids = {row.id for row in owned_query.all()}
    missing_ids = [source_id for source_id in normalized if source_id not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Selected sources not found or unauthorized: {', '.join(missing_ids)}",
        )
    return normalized


async def _prepare_chat_turn(
    db: Session,
    request: ChatRequest,
    current_user: User,
    timings: ChatTiming,
    selected_source_ids: list[str],
) -> ChatTurn:
    normalized = _validate_message(request.message)
    conversation = get_or_create_conversation(
        db,
        current_user,
        conversation_id=request.conversation_id,
        notebook_id=request.notebook_id,
    )
    history_started = time.perf_counter()
    recent_history = load_recent_history(db, conversation.id)
    timings.history_load_ms = _elapsed_ms(history_started)
    history = _history_payload(recent_history)
    rewrite_started = time.perf_counter()
    rewritten_query = await chat_runtime_service.rewrite_question(normalized, history)
    timings.rewrite_ms = _elapsed_ms(rewrite_started)
    retrieval_started = time.perf_counter()
    is_community = False
    if request.notebook_id is not None:
        nb = db.query(Notebook).filter(Notebook.id == request.notebook_id).first()
        is_community = nb is not None and nb.is_community
    contexts = chat_runtime_service.retrieve(
        db,
        rewritten_query,
        pipeline_version=settings.pipeline_version,
        user_id=current_user.id,
        notebook_id=request.notebook_id,
        selected_source_ids=selected_source_ids,
        is_community=is_community,
    )
    timings.retrieval_ms = _elapsed_ms(retrieval_started)
    available_citations = chat_runtime_service.citations_from_context(contexts)
    save_chat_message(
        db,
        conversation.id,
        role="user",
        content=normalized,
        rewritten_query=rewritten_query,
    )
    return ChatTurn(
        conversation_id=conversation.id,
        message=normalized,
        recent_history=history,
        rewritten_query=rewritten_query,
        contexts=contexts,
        available_citations=available_citations,
    )


async def _chat_non_stream_impl(
    db: Session,
    request: ChatRequest,
    current_user: User,
    *,
    selected_source_ids: list[str],
) -> ChatResponse:
    timings = ChatTiming()
    if request.notebook_id is not None and not _has_ready_notebook_documents(
        db,
        user_id=current_user.id,
        notebook_id=request.notebook_id,
    ):
        conversation = get_or_create_conversation(
            db,
            current_user,
            conversation_id=request.conversation_id,
            notebook_id=request.notebook_id,
        )
        user_message = save_chat_message(
            db,
            conversation.id,
            role="user",
            content=_validate_message(request.message),
            rewritten_query=_validate_message(request.message),
        )
        return ChatResponse(
            answer=EMPTY_NOTEBOOK_ANSWER,
            citations=[],
            conversation_id=conversation.id,
            message_id=user_message.id,
            rewritten_query=_validate_message(request.message),
        )

    turn = await _prepare_chat_turn(db, request, current_user, timings, selected_source_ids)

    try:
        answer, _provider = await chat_runtime_service.answer(
            turn.message,
            turn.contexts,
            turn.recent_history,
            db=db,
            user_id=current_user.username,
        )
    except Exception as exc:
        logger.error("chat_non_stream_failed: %s", str(exc), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate answer")

    answer = chat_runtime_service.normalize_citation_markers(answer, turn.available_citations)
    used_citations = chat_runtime_service.filter_citations_for_answer(answer, turn.available_citations)
    assistant_message = save_chat_message(
        db,
        turn.conversation_id,
        role="assistant",
        content=answer,
        sources_used=used_citations,
    )

    return ChatResponse(
        answer=answer,
        citations=used_citations,
        conversation_id=turn.conversation_id,
        message_id=assistant_message.id,
        rewritten_query=turn.rewritten_query,
    )


def _sse_payload(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _final_payload(
    *,
    answer: str,
    citations: list[dict] | None,
    conversation_id: str | None,
    message_id: str | None,
    rewritten_query: str,
    error: str | None = None,
) -> dict:
    payload = {
        "type": "final",
        "token": "",
        "done": True,
        "answer": answer,
        "citations": citations or [],
        "conversation_id": conversation_id,
        "message_id": message_id,
        "rewritten_query": rewritten_query,
    }
    if error:
        payload["error"] = error
    return payload


def _log_chat_stream(
    level: str,
    message: str,
    *,
    request_id: str | None,
    current_user: User,
    request: ChatRequest,
    conversation_id: str | None,
    timings: ChatTiming,
) -> None:
    log_api_event(
        level,
        message,
        request_id=request_id,
        user_id=current_user.id,
        conversation_id=conversation_id,
        notebook_id=request.notebook_id,
        history_load_ms=timings.history_load_ms,
        rewrite_ms=timings.rewrite_ms,
        retrieval_ms=timings.retrieval_ms,
        llm_first_token_ms=timings.llm_first_token_ms,
        total_stream_ms=timings.total_stream_ms,
        error_stage=timings.error_stage,
    )


@router.post("/api/chat", response_model=ChatResponse)
async def chat_api(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    selected_source_ids = _resolve_selected_source_ids(db, request, current_user)
    return await _chat_non_stream_impl(
        db,
        request,
        current_user,
        selected_source_ids=selected_source_ids,
    )




async def _chat_stream_impl(
    db: Session,
    request: ChatRequest,
    current_user: User,
    request_id: str | None,
    http_request: Request,
    *,
    selected_source_ids: list[str],
):
    async def event_generator():
        timings = ChatTiming()
        stream_started = time.perf_counter()
        conversation_id: str | None = None
        rewritten_query = request.message
        answer_parts: list[str] = []
        yield _sse_payload({"type": "status", "token": "", "done": False, "stage": "accepted"})

        try:
            if await http_request.is_disconnected():
                timings.total_stream_ms = _elapsed_ms(stream_started)
                _log_chat_stream(
                    "info",
                    "chat_stream_cancelled",
                    request_id=request_id,
                    current_user=current_user,
                    request=request,
                    conversation_id=conversation_id,
                    timings=timings,
                )
                return
            if request.notebook_id is not None and not _has_ready_notebook_documents(
                db,
                user_id=current_user.id,
                notebook_id=request.notebook_id,
            ):
                timings.error_stage = "empty_notebook_guard"
                conversation = get_or_create_conversation(
                    db,
                    current_user,
                    conversation_id=request.conversation_id,
                    notebook_id=request.notebook_id,
                )
                conversation_id = conversation.id
                rewritten_query = _validate_message(request.message)
                user_message = save_chat_message(
                    db,
                    conversation.id,
                    role="user",
                    content=rewritten_query,
                    rewritten_query=rewritten_query,
                )
                timings.total_stream_ms = _elapsed_ms(stream_started)
                _log_chat_stream(
                    "info",
                    "chat_stream_empty_notebook",
                    request_id=request_id,
                    current_user=current_user,
                    request=request,
                    conversation_id=conversation_id,
                    timings=timings,
                )
                yield _sse_payload(
                    _final_payload(
                        answer=EMPTY_NOTEBOOK_ANSWER,
                        citations=[],
                        conversation_id=conversation_id,
                        message_id=user_message.id,
                        rewritten_query=rewritten_query,
                    )
                )
                return

            timings.error_stage = "prepare"
            turn = await _prepare_chat_turn(
                db,
                request,
                current_user,
                timings,
                selected_source_ids,
            )
            conversation_id = turn.conversation_id
            rewritten_query = turn.rewritten_query
            timings.error_stage = "llm_stream"
            llm_started = time.perf_counter()
            async for token in chat_runtime_service.stream_answer(
                turn.message,
                turn.contexts,
                turn.recent_history,
                db=db,
                user_id=current_user.username,
            ):
                if await http_request.is_disconnected():
                    timings.total_stream_ms = _elapsed_ms(stream_started)
                    _log_chat_stream(
                        "info",
                        "chat_stream_cancelled",
                        request_id=request_id,
                        current_user=current_user,
                        request=request,
                        conversation_id=conversation_id,
                        timings=timings,
                    )
                    return
                answer_parts.append(token)
                if timings.llm_first_token_ms is None:
                    timings.llm_first_token_ms = _elapsed_ms(llm_started)
                yield _sse_payload({"type": "token", "token": token, "done": False})

            answer = "".join(answer_parts)
            answer = chat_runtime_service.normalize_citation_markers(answer, turn.available_citations)
            timings.error_stage = "save_assistant"
            used_citations = chat_runtime_service.filter_citations_for_answer(answer, turn.available_citations)
            assistant_message = save_chat_message(
                db,
                turn.conversation_id,
                role="assistant",
                content=answer,
                sources_used=used_citations,
            )
            timings.error_stage = None
            timings.total_stream_ms = _elapsed_ms(stream_started)
            _log_chat_stream(
                "info",
                "chat_stream_completed",
                request_id=request_id,
                current_user=current_user,
                request=request,
                conversation_id=turn.conversation_id,
                timings=timings,
            )
            yield _sse_payload(
                _final_payload(
                    answer=answer,
                    citations=used_citations,
                    conversation_id=turn.conversation_id,
                    message_id=assistant_message.id,
                    rewritten_query=turn.rewritten_query,
                )
            )
        except Exception as exc:
            logger.error("chat_stream_failed: %s", str(exc), exc_info=True)
            timings.total_stream_ms = _elapsed_ms(stream_started)
            _log_chat_stream(
                "error",
                "chat_stream_failed",
                request_id=request_id,
                current_user=current_user,
                request=request,
                conversation_id=conversation_id,
                timings=timings,
            )
            yield _sse_payload(
                _final_payload(
                    answer=CHAT_ERROR_ANSWER,
                    citations=[],
                    conversation_id=conversation_id,
                    message_id=None,
                    rewritten_query=rewritten_query,
                    error="chat_stream_failed",
                )
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/api/chat/stream")
async def chat_stream_api(
    http_request: Request,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    selected_source_ids = _resolve_selected_source_ids(db, request, current_user)
    return await _chat_stream_impl(
        db,
        request,
        current_user,
        request_id=getattr(http_request.state, "request_id", None),
        http_request=http_request,
        selected_source_ids=selected_source_ids,
    )
