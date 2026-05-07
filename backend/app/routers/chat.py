"""
chat.py — Router for RAG chat with SSE streaming.

POST /chat/stream — Accept a JSON body with { "message": "..." },
                    return a text/event-stream response that streams
                    answer tokens from the LLM.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream a RAG-augmented answer using Server-Sent Events (SSE).

    The client sends a JSON body: { "message": "user question here" }
    The response is a text/event-stream where each event contains a
    chunk of the answer text.

    SSE format:
      data: {"token": "chunk of text"}

      data: {"token": "", "done": true}
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty.",
        )

    async def event_generator():
        try:
            async for chunk in rag_service.stream_answer(request.message.strip()):
                # Send each token as an SSE data event
                payload = json.dumps({"token": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

            # Send done signal
            done_payload = json.dumps({"token": "", "done": True})
            yield f"data: {done_payload}\n\n"

        except Exception as e:
            logger.error(f"[Chat SSE] Error: {e}", exc_info=True)
            error_payload = json.dumps(
                {"token": f"\n\n⚠️ Lỗi: {str(e)}", "done": True},
                ensure_ascii=False,
            )
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
