from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from .settings import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    if not settings.smtp_host:
        logger.info("SMTP not configured — printing code to console for %s", to)
        print(f"[MOCK SMTP] To: {to} - Your code is: {body}")
        return

    msg = EmailMessage()
    msg["From"] = settings.email_from or settings.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        raise RuntimeError(f"Failed to send email: {exc}") from exc
