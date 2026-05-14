from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from ..core.settings import settings


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "service": settings.service_name,
            "level": record.levelname.lower(),
            "ts": datetime.now(timezone.utc).isoformat(),
            "message": record.getMessage(),
        }

        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)

        return json.dumps(payload, ensure_ascii=False)



def get_worker_logger() -> logging.Logger:
    logger = logging.getLogger("ingest_worker")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = get_worker_logger()



def log_event(level: str, message: str, **fields: Any) -> None:
    safe_fields = {
        key: value
        for key, value in fields.items()
        if value is not None
    }
    level_value = level.lower()
    if level_value == "debug":
        logger.debug(message, extra={"extra_fields": safe_fields})
    elif level_value == "warning":
        logger.warning(message, extra={"extra_fields": safe_fields})
    elif level_value == "error":
        logger.error(message, extra={"extra_fields": safe_fields})
    else:
        logger.info(message, extra={"extra_fields": safe_fields})
