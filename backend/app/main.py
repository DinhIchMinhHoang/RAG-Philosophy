from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import models
from .core.logging_utils import log_api_event
from .core.security import validate_secret_key
from .database import engine
from .routers import admin, auth, chat, documents, ingest, notebooks

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lumina RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup_validate_security() -> None:
    validate_secret_key()


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_api_event(
            "error",
            "request_failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms,
            error_message=str(exc),
        )
        raise

    duration_ms = int((time.perf_counter() - start) * 1000)
    response.headers["X-Request-Id"] = request_id
    log_api_event(
        "info",
        "request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


def _error_envelope(*, request: Request, status_code: int, code: str, message: str, details=None):
    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(request.state, "request_id", None),
        },
        "detail": message,
    }
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    details = exc.detail if not isinstance(exc.detail, str) else None
    return _error_envelope(
        request=request,
        status_code=exc.status_code,
        code=f"http_{exc.status_code}",
        message=message,
        details=details,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_envelope(
        request=request,
        status_code=422,
        code="validation_error",
        message="Request validation failed",
        details=exc.errors(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log_api_event(
        "error",
        "unhandled_exception",
        request_id=getattr(request.state, "request_id", None),
        method=request.method,
        path=request.url.path,
        error_message=str(exc),
    )
    return _error_envelope(
        request=request,
        status_code=500,
        code="internal_error",
        message="Internal server error",
    )


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(documents.router)
app.include_router(admin.router)
app.include_router(notebooks.router)


@app.get("/")
def root():
    return {"message": "Welcome to Lumina RAG"}
