from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import ChatMessage, Conversation, Notebook, User

RECENT_HISTORY_LIMIT = 4
RECENT_HISTORY_CHAR_BUDGET = 4000


@dataclass(frozen=True)
class RecentChatMessage:
    role: str
    content: str


def _validate_notebook_access(db: Session, notebook_id: int, user: User) -> Notebook:
    notebook = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if notebook.owner_id != user.id and not notebook.is_community:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to use this notebook")
    return notebook


def get_or_create_conversation(
    db: Session,
    user: User,
    *,
    conversation_id: str | None = None,
    notebook_id: int | None = None,
) -> Conversation:
    if conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.owner_id == user.id)
            .first()
        )
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        if notebook_id is not None and conversation.notebook_id != notebook_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversation_id does not belong to notebook_id",
            )
        return conversation

    if notebook_id is not None:
        _validate_notebook_access(db, notebook_id, user)

    conversation = Conversation(owner_id=user.id, notebook_id=notebook_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def load_recent_history(
    db: Session,
    conversation_id: str,
    *,
    limit: int = RECENT_HISTORY_LIMIT,
    char_budget: int = RECENT_HISTORY_CHAR_BUDGET,
) -> list[RecentChatMessage]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(limit)
        .all()
    )

    recent: list[RecentChatMessage] = []
    remaining = char_budget
    for row in reversed(rows):
        content = row.content.strip()
        if not content:
            continue
        if len(content) > remaining:
            content = content[:remaining]
        if not content:
            break
        recent.append(RecentChatMessage(role=row.role, content=content))
        remaining -= len(content)
        if remaining <= 0:
            break
    return recent


def save_chat_message(
    db: Session,
    conversation_id: str,
    *,
    role: str,
    content: str,
    sources_used: list[dict] | None = None,
    rewritten_query: str | None = None,
) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources_used=sources_used,
        rewritten_query=rewritten_query,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
