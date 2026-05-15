from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models
from .security import decode_access_token

ADMIN_EMAIL_SUFFIX = "@lumina.com.vn"


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(database.get_db),
) -> models.User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization[7:]
    username = decode_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return db_user


def require_admin_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    email = (current_user.email or "").lower()
    if not email.endswith(ADMIN_EMAIL_SUFFIX):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
