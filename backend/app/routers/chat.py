from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..core.dependencies import get_current_user
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


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    notebook_id: int | None = None


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


def _validate_message(message: str) -> str:
    if not message or not message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    return message.strip()


def _history_payload(recent_history: list[RecentChatMessage]) -> list[dict[str, str]]:
    return [{"role": item.role, "content": item.content} for item in recent_history]


async def _prepare_chat_turn(db: Session, request: ChatRequest, current_user: User) -> ChatTurn:
    normalized = _validate_message(request.message)
    conversation = get_or_create_conversation(
        db,
        current_user,
        conversation_id=request.conversation_id,
        notebook_id=request.notebook_id,
    )
    recent_history = load_recent_history(db, conversation.id)
    history = _history_payload(recent_history)
    rewritten_query = await chat_runtime_service.rewrite_question(normalized, history)
    contexts = chat_runtime_service.retrieve(db, rewritten_query, pipeline_version=settings.pipeline_version)
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


async def _chat_non_stream_impl(db: Session, request: ChatRequest, current_user: User) -> ChatResponse:
    turn = await _prepare_chat_turn(db, request, current_user)

    try:
        answer, _provider = await chat_runtime_service.answer(
            turn.message,
            turn.contexts,
            turn.recent_history,
        )
    except Exception as exc:
        logger.error("chat_non_stream_failed: %s", str(exc), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate answer")

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


@router.post("/api/chat", response_model=ChatResponse)
async def chat_api(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _chat_non_stream_impl(db, request, current_user)




async def _chat_stream_impl(db: Session, request: ChatRequest, current_user: User):
    turn = await _prepare_chat_turn(db, request, current_user)
    answer_parts: list[str] = []

    async def event_generator():
        try:
            async for token in chat_runtime_service.stream_answer(
                turn.message,
                turn.contexts,
                turn.recent_history,
            ):
                answer_parts.append(token)
                payload = json.dumps({"type": "token", "token": token, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

            answer = "".join(answer_parts)
            used_citations = chat_runtime_service.filter_citations_for_answer(answer, turn.available_citations)
            assistant_message = save_chat_message(
                db,
                turn.conversation_id,
                role="assistant",
                content=answer,
                sources_used=used_citations,
            )
            final_payload = json.dumps(
                {
                    "type": "final",
                    "token": "",
                    "done": True,
                    "answer": answer,
                    "citations": used_citations,
                    "conversation_id": turn.conversation_id,
                    "message_id": assistant_message.id,
                    "rewritten_query": turn.rewritten_query,
                },
                ensure_ascii=False,
            )
            yield f"data: {final_payload}\n\n"
        except Exception as exc:
            logger.error("chat_stream_failed: %s", str(exc), exc_info=True)
            error_payload = json.dumps(
                {
                    "type": "error",
                    "token": "",
                    "done": True,
                    "error": "Failed to generate answer",
                    "citations": [],
                    "conversation_id": turn.conversation_id,
                    "rewritten_query": turn.rewritten_query,
                },
                ensure_ascii=False,
            )
            yield f"data: {error_payload}\n\n"

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
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _chat_stream_impl(db, request, current_user)
