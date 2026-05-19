from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..core.dependencies import get_current_user
from ..core.settings import settings
from ..services.chat_runtime import chat_runtime_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[dict]


def _validate_message(message: str) -> str:
    if not message or not message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    return message.strip()


async def _chat_non_stream_impl(db: Session, message: str, current_user: User | None = None) -> ChatResponse:
    normalized = _validate_message(message)
    contexts = chat_runtime_service.retrieve(
        db,
        normalized,
        pipeline_version=settings.pipeline_version,
        user_id=current_user.username if current_user else None,
    )
    citations = chat_runtime_service.citations_from_context(contexts)

    try:
        answer, _provider = await chat_runtime_service.answer(normalized, contexts)
    except Exception as exc:
        logger.error("chat_non_stream_failed: %s", str(exc), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate answer")

    return ChatResponse(answer=answer, citations=citations)


@router.post("/api/chat", response_model=ChatResponse)
async def chat_api(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _chat_non_stream_impl(db, request.message, current_user)




async def _chat_stream_impl(db: Session, message: str, current_user: User | None = None):
    normalized = _validate_message(message)
    contexts = chat_runtime_service.retrieve(
        db,
        normalized,
        pipeline_version=settings.pipeline_version,
        user_id=current_user.username if current_user else None,
    )
    citations = chat_runtime_service.citations_from_context(contexts)

    answer_parts: list[str] = []

    async def event_generator():
        try:
            async for token in chat_runtime_service.stream_answer(normalized, contexts):
                answer_parts.append(token)
                payload = json.dumps({"type": "token", "token": token, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

            final_payload = json.dumps(
                {
                    "type": "final",
                    "token": "",
                    "done": True,
                    "answer": "".join(answer_parts),
                    "citations": citations,
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
    return await _chat_stream_impl(db, request.message, current_user)

