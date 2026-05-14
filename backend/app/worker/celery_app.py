from __future__ import annotations

from celery import Celery
from celery.signals import worker_process_init

from ..core.settings import settings
from ..ingest.logging_utils import log_event
from ..ingest.runtime import validate_worker_environment


celery_app = Celery(
    "ingest_worker",
    broker=settings.redis_broker_url,
    backend=settings.redis_result_backend,
    include=["backend.app.worker.tasks"],
)

celery_app.conf.update(
    task_default_queue=settings.celery_ingest_queue,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    result_expires=3600,
    task_routes={
        "backend.app.worker.tasks.process_ingest_job": {"queue": settings.celery_ingest_queue},
    },
)


@worker_process_init.connect
def _validate_runtime(**kwargs):
    validate_worker_environment()
    log_event(
        "info",
        "worker_runtime_validated",
        stage="startup",
    )
