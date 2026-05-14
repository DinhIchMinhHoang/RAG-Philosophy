from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

from .settings import settings

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "khoa_du_phong_neu_quen_tao_env")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

_WEAK_SECRET_VALUES = {
    "",
    "khoa_du_phong_neu_quen_tao_env",
    "change-this-secret-in-production",
    "changeme",
    "secret",
    "default",
}


def validate_secret_key() -> None:
    if settings.app_env in {"development", "dev", "local", "test"}:
        return
    normalized = (SECRET_KEY or "").strip().lower()
    if normalized in _WEAK_SECRET_VALUES:
        raise RuntimeError(
            "SECRET_KEY is empty or using a known weak default in non-development environment."
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Union[str, None]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
