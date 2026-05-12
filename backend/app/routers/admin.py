from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from .auth import require_admin, get_current_user


router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user_admin(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")

    # Create user; by default is_admin remains False unless client sets it separately via another endpoint.
    from ..core import security as _sec
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=_sec.get_password_hash(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None
