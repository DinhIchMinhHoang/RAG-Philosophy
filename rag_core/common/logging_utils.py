from __future__ import annotations

import logging

_DEFAULT_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if getattr(root, "_rag_configured", False):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
    root.addHandler(handler)
    root.setLevel(level)
    setattr(root, "_rag_configured", True)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
