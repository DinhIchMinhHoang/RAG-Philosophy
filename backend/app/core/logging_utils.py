from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from .settings import settings


SENSITIVE_KEYS = {"authorization", "password", "token", "secret", "api_key", "access_token"}


class ApiJsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "service": settings.api_service_name,
            "level": record.levelname.lower(),
            "ts": datetime.now(timezone.utc).isoformat(),
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(_sanitize(extra))
        return json.dumps(payload, ensure_ascii=False)


def _sanitize(fields: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in fields.items():
        if key.lower() in SENSITIVE_KEYS:
            continue
        safe[key] = value
    return safe


def get_api_logger() -> logging.Logger:
    logger = logging.getLogger("backend_api")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(ApiJsonLogFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


api_logger = get_api_logger()


def log_api_event(level: str, message: str, **fields: Any) -> None:
    payload = _sanitize({k: v for k, v in fields.items() if v is not None})
    level_value = level.lower()
    if level_value == "debug":
        api_logger.debug(message, extra={"extra_fields": payload})
    elif level_value == "warning":
        api_logger.warning(message, extra={"extra_fields": payload})
    elif level_value == "error":
        api_logger.error(message, extra={"extra_fields": payload})
    else:
        api_logger.info(message, extra={"extra_fields": payload})
