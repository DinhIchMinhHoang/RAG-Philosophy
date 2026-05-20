from __future__ import annotations

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


def _visible_notebooks_query(db: Session, user_id: int) -> Query[models.Notebook]:
    return db.query(models.Notebook).filter(
        (models.Notebook.owner_id == user_id) | (models.Notebook.is_community == 1)
    )


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
