from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Query, Session

from .. import database, models
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/api/notebooks", tags=["Notebooks"])


class NotebookCreate(BaseModel):
    title: str
    is_community: bool = False


class NotebookUpdate(BaseModel):
    title: str | None = None
    cover_url: str | None = None
    cover_mode: str | None = None
    cover_color: str | None = None


class NotebookResponse(BaseModel):
    id: int
    title: str
    owner_id: int
    is_community: bool
    cover_url: str | None
    cover_mode: str | None
    cover_color: str | None
    created_at: str


class ConversationSummaryResponse(BaseModel):
    id: str
    notebook_id: int | None
    owner_id: int
    created_at: str
    updated_at: str


class ConversationMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources_used: list[dict] | None
    rewritten_query: str | None
    created_at: str


class LatestConversationResponse(BaseModel):
    conversation: ConversationSummaryResponse | None
    messages: list[ConversationMessageResponse]
    has_conversation: bool
    limit: int


class SavedNotebookItemCreate(BaseModel):
    kind: Literal["note", "pin", "conversation", "summary"]
    content: str
    title: str | None = None
    conversation_id: str | None = None
    message_id: str | None = None
    sources_used: list[dict] | None = None


class SavedNotebookItemResponse(BaseModel):
    id: str
    notebook_id: int
    kind: str
    title: str | None
    content: str
    conversation_id: str | None
    message_id: str | None
    sources_used: list[dict] | None
    created_at: str


def _notebook_response(notebook: models.Notebook) -> NotebookResponse:
    return NotebookResponse(
        id=notebook.id,
        title=notebook.title,
        owner_id=notebook.owner_id,
        is_community=bool(notebook.is_community),
        cover_url=notebook.cover_url,
        cover_mode=notebook.cover_mode,
        cover_color=notebook.cover_color,
        created_at=notebook.created_at.isoformat(),
    )


def _conversation_response(conversation: models.Conversation) -> ConversationSummaryResponse:
    return ConversationSummaryResponse(
        id=conversation.id,
        notebook_id=conversation.notebook_id,
        owner_id=conversation.owner_id,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )


def _message_response(message: models.ChatMessage) -> ConversationMessageResponse:
    return ConversationMessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        sources_used=message.sources_used,
        rewritten_query=message.rewritten_query,
        created_at=message.created_at.isoformat(),
    )


def _saved_item_response(item: models.SavedNotebookItem) -> SavedNotebookItemResponse:
    return SavedNotebookItemResponse(
        id=item.id,
        notebook_id=item.notebook_id,
        kind=item.kind,
        title=item.title,
        content=item.content,
        conversation_id=item.conversation_id,
        message_id=item.message_id,
        sources_used=item.sources_used,
        created_at=item.created_at.isoformat(),
    )


def _visible_notebooks_query(db: Session, user_id: int) -> Query[models.Notebook]:
    return db.query(models.Notebook).filter(
        (models.Notebook.owner_id == user_id) | (models.Notebook.is_community == 1)
    )


def _get_visible_notebook(db: Session, notebook_id: int, user_id: int) -> models.Notebook:
    notebook = _visible_notebooks_query(db, user_id).filter(models.Notebook.id == notebook_id).first()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    return notebook


@router.get("", response_model=list[NotebookResponse])
def list_notebooks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    notebooks = _visible_notebooks_query(db, current_user.id).order_by(models.Notebook.created_at.desc()).all()
    return [_notebook_response(notebook) for notebook in notebooks]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NotebookResponse)
def create_notebook(
    payload: NotebookCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = models.Notebook(
        title=payload.title,
        owner_id=current_user.id,
        is_community=1 if payload.is_community else 0,
    )
    db.add(nb)
    db.commit()
    db.refresh(nb)
    return _notebook_response(nb)


@router.get("/{notebook_id}/conversations/latest", response_model=LatestConversationResponse)
def get_latest_notebook_conversation(
    notebook_id: int,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    _get_visible_notebook(db, notebook_id, current_user.id)
    limit = max(1, min(limit, 100))
    conversation = (
        db.query(models.Conversation)
        .filter(
            models.Conversation.owner_id == current_user.id,
            models.Conversation.notebook_id == notebook_id,
            models.Conversation.archived_at.is_(None),
        )
        .order_by(models.Conversation.updated_at.desc(), models.Conversation.created_at.desc())
        .first()
    )
    if conversation is None:
        return LatestConversationResponse(conversation=None, messages=[], has_conversation=False, limit=limit)

    rows = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.conversation_id == conversation.id)
        .order_by(models.ChatMessage.created_at.desc(), models.ChatMessage.id.desc())
        .limit(limit)
        .all()
    )
    messages = [_message_response(message) for message in reversed(rows)]
    return LatestConversationResponse(
        conversation=_conversation_response(conversation),
        messages=messages,
        has_conversation=True,
        limit=limit,
    )


@router.post("/{notebook_id}/notes", status_code=status.HTTP_201_CREATED, response_model=SavedNotebookItemResponse)
def create_saved_notebook_item(
    notebook_id: int,
    payload: SavedNotebookItemCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    _get_visible_notebook(db, notebook_id, current_user.id)
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Saved item content cannot be empty")

    if payload.conversation_id is not None:
        conversation = (
            db.query(models.Conversation)
            .filter(
                models.Conversation.id == payload.conversation_id,
                models.Conversation.owner_id == current_user.id,
                models.Conversation.notebook_id == notebook_id,
            )
            .first()
        )
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if payload.message_id is not None:
        message = (
            db.query(models.ChatMessage)
            .join(models.Conversation, models.Conversation.id == models.ChatMessage.conversation_id)
            .filter(
                models.ChatMessage.id == payload.message_id,
                models.Conversation.owner_id == current_user.id,
                models.Conversation.notebook_id == notebook_id,
            )
            .first()
        )
        if message is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    item = models.SavedNotebookItem(
        owner_id=current_user.id,
        notebook_id=notebook_id,
        conversation_id=payload.conversation_id,
        message_id=payload.message_id,
        kind=payload.kind,
        title=payload.title,
        content=content,
        sources_used=payload.sources_used,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _saved_item_response(item)


@router.patch("/{notebook_id}", response_model=NotebookResponse)
def update_notebook(
    notebook_id: int,
    payload: NotebookUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")
    if payload.title is not None:
        nb.title = payload.title
    if payload.cover_url is not None:
        nb.cover_url = payload.cover_url
    if payload.cover_mode is not None:
        nb.cover_mode = payload.cover_mode
    if payload.cover_color is not None:
        nb.cover_color = payload.cover_color
    db.commit()
    db.refresh(nb)
    return _notebook_response(nb)


@router.delete("/{notebook_id}")
def delete_notebook(
    notebook_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")
    db.delete(nb)
    db.commit()
    return {"deleted": True}
