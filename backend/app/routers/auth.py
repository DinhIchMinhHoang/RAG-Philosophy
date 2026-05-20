from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, schemas
from ..core.dependencies import get_current_user
from ..core.security import create_access_token, get_password_hash, verify_password

router = APIRouter(tags=["Authentication"])


def _create_user(user: schemas.UserCreate, db: Session) -> schemas.Token:
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already used")

    db_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(subject=new_user.username)
    return schemas.Token(access_token=access_token, token_type="bearer")


def _login_user(user: schemas.UserLogin, db: Session) -> schemas.Token:
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(subject=db_user.username)
    return schemas.Token(access_token=access_token, token_type="bearer")


def _change_password(change_pwd: schemas.ChangePassword, current_user: models.User, db: Session) -> dict[str, str]:
    if not verify_password(change_pwd.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    if change_pwd.current_password == change_pwd.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    current_user.hashed_password = get_password_hash(change_pwd.new_password)
    db.add(current_user)
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/api/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.Token)
def signup_api(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    return _create_user(user, db)


@router.post("/api/login", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login_api(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    return _login_user(user, db)


@router.post("/api/change-password", status_code=status.HTTP_200_OK)
def change_password_api(
    change_pwd: schemas.ChangePassword,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    return _change_password(change_pwd, current_user, db)
