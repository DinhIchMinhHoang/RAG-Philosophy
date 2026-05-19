from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models
from ..core.dependencies import get_current_user

router = APIRouter(prefix="/api/notebooks", tags=["Notebooks"])


class NotebookCreate(BaseModel):
    name: str
    is_community: bool = False


class NotebookUpdate(BaseModel):
    title: str | None = None
    cover_url: str | None = None
    cover_mode: str | None = None
    cover_color: str | None = None


class NotebookResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    is_community: bool
    cover_url: str | None
    cover_mode: str | None
    cover_color: str | None
    created_at: str


@router.get("", response_model=list[NotebookResponse])
def list_notebooks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = db.query(models.Notebook).filter(
        (models.Notebook.user_id == current_user.id) | models.Notebook.is_community
    ).order_by(models.Notebook.created_at.desc()).all()
    return [
        NotebookResponse(
            id=n.id, name=n.name, owner_id=n.user_id, is_community=bool(n.is_community),
            cover_url=n.cover_url, cover_mode=n.cover_mode, cover_color=n.cover_color,
            created_at=n.created_at.isoformat(),
        )
        for n in nb
    ]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NotebookResponse)
def create_notebook(
    payload: NotebookCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    # Create notebook entry first to obtain an id, then create filesystem structure and update paths
    nb = models.Notebook(name=payload.name, user_id=current_user.id, is_community=payload.is_community,
                         notebook_dir="", vector_db_path="")
    db.add(nb)
    db.commit()
    db.refresh(nb)

    # create directories
    from ..core.fs_utils import ensure_notebook_dirs
    from ..core.settings import settings

    data_root = settings.object_storage_local_root
    paths = ensure_notebook_dirs(data_root, current_user.id, nb.id)

    nb.notebook_dir = paths["notebook_dir"]
    nb.vector_db_path = paths["vector_db_path"]
    db.add(nb)

    # ensure user's root dir stored
    if not current_user.user_root_dir:
        current_user.user_root_dir = paths["user_root_dir"]
        db.add(current_user)

    db.commit()
    db.refresh(nb)

    return NotebookResponse(
        id=nb.id, name=nb.name, owner_id=nb.user_id, is_community=bool(nb.is_community),
        cover_url=nb.cover_url, cover_mode=nb.cover_mode, cover_color=nb.cover_color,
        created_at=nb.created_at.isoformat(),
    )


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
    if nb.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")
    if payload.title is not None:
        nb.name = payload.title
    if payload.cover_url is not None:
        nb.cover_url = payload.cover_url
    if payload.cover_mode is not None:
        nb.cover_mode = payload.cover_mode
    if payload.cover_color is not None:
        nb.cover_color = payload.cover_color
    db.commit()
    db.refresh(nb)
    return NotebookResponse(
        id=nb.id, name=nb.name, owner_id=nb.user_id, is_community=bool(nb.is_community),
        cover_url=nb.cover_url, cover_mode=nb.cover_mode, cover_color=nb.cover_color,
        created_at=nb.created_at.isoformat(),
    )


@router.delete("/{notebook_id}")
def delete_notebook(
    notebook_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    nb = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
    if nb.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")
    db.delete(nb)
    db.commit()
    return {"deleted": True}
