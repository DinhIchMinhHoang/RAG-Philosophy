from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, schemas
from ..core.security import get_password_hash

router = APIRouter(tags=["Authentication"])

# Configurable TTL in minutes
PASSWORD_CODE_TTL_MINUTES = 15


def _generate_code(length: int = 6) -> str:
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))


@router.post("/api/password/forgot", status_code=status.HTTP_200_OK)
def request_password_reset(req: schemas.PasswordForgotRequest, db: Session = Depends(database.get_db)):
    # Always respond with generic message to avoid user enumeration
    db_user = db.query(models.User).filter(models.User.email == req.email).first()
    if not db_user:
        # do not reveal existence
        return {"message": "If an account exists for this email, a verification code has been sent."}

    code = _generate_code(6)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_CODE_TTL_MINUTES)

    pr = models.PasswordResetCode(email=req.email, verification_code=code, expires_at=expires_at)
    db.add(pr)
    db.commit()

    # Mock SMTP: print to console
    print(f"[MOCK SMTP] To: {req.email} - Your verification code is: {code}")

    return {"message": "If an account exists for this email, a verification code has been sent."}


@router.post("/api/password/verify", status_code=status.HTTP_200_OK)
def verify_password_code(req: schemas.PasswordVerifyRequest, db: Session = Depends(database.get_db)):
    now = datetime.now(timezone.utc)
    row = (
        db.query(models.PasswordResetCode)
        .filter(models.PasswordResetCode.email == req.email)
        .filter(models.PasswordResetCode.expires_at > now)
        .order_by(models.PasswordResetCode.created_at.desc())
        .first()
    )
    if not row or row.verification_code != req.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")

    return {"verified": True}


@router.post("/api/password/reset", status_code=status.HTTP_200_OK)
def reset_password(req: schemas.PasswordResetRequest, db: Session = Depends(database.get_db)):
    now = datetime.now(timezone.utc)
    row = (
        db.query(models.PasswordResetCode)
        .filter(models.PasswordResetCode.email == req.email)
        .filter(models.PasswordResetCode.expires_at > now)
        .order_by(models.PasswordResetCode.created_at.desc())
        .first()
    )
    if not row or row.verification_code != req.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")

    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    user.hashed_password = get_password_hash(req.new_password)
    db.add(user)

    # delete all codes for this email (spent)
    db.query(models.PasswordResetCode).filter(models.PasswordResetCode.email == req.email).delete()

    db.commit()
    return {"message": "Password reset successful"}
