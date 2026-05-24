from __future__ import annotations

from typing import Final

from ..models import JobStage, JobStatus

VALID_JOB_STATUSES: Final[set[str]] = {status.value for status in JobStatus}
VALID_JOB_STAGES: Final[set[str]] = {stage.value for stage in JobStage}

STAGE_PROGRESS_RANGES: Final[dict[str, tuple[int, int]]] = {
    JobStage.FETCHING_OBJECT.value: (0, 10),
    JobStage.PARSING.value: (10, 35),
    JobStage.CHUNKING.value: (35, 55),
    JobStage.EMBEDDING.value: (55, 80),
    JobStage.INDEXING_VECTOR.value: (80, 95),
    JobStage.PERSISTING_METADATA.value: (95, 99),
    JobStage.LOADING_SQL.value: (99, 100),
}

STAGE_ORDER: Final[list[str]] = [
    JobStage.FETCHING_OBJECT.value,
    JobStage.PARSING.value,
    JobStage.CHUNKING.value,
    JobStage.EMBEDDING.value,
    JobStage.INDEXING_VECTOR.value,
    JobStage.PERSISTING_METADATA.value,
    JobStage.LOADING_SQL.value,
]

MAX_FILE_SIZE_MB: Final[int] = 50
BATCH_SIZE: Final[int] = 500
HEADER_CHECK_ROWS: Final[int] = 20
HEADER_MIN_NONEMPTY_RATIO: Final[float] = 0.5
TABLE_PREFIX: Final[str] = "etbl"
TABLE_NAME_MAX_LEN: Final[int] = 56
SQL_MAX_ROWS: Final[int] = 200
SQL_MAX_RETRIES: Final[int] = 3
MAX_LLM_RETRIES: Final[int] = 2
SAMPLE_ROW_COUNT: Final[int] = 3
DOCX_WORDS_PER_VIRTUAL_PAGE: Final[int] = 700


def stage_progress(stage: str, ratio: float) -> int:
    if stage not in STAGE_PROGRESS_RANGES:
        raise ValueError(f"Unsupported stage: {stage}")

    start, end = STAGE_PROGRESS_RANGES[stage]
    clamped_ratio = max(0.0, min(1.0, ratio))
    value = start + int((end - start) * clamped_ratio)
    return min(max(value, start), end)
