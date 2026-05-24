from __future__ import annotations

import json
import re
import logging
from difflib import SequenceMatcher
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..ingest.constants import SQL_MAX_ROWS, MAX_LLM_RETRIES
from ..models import ExcelTableRecord
from .excel_schema import build_column_profile, compact_text, normalize_text

logger = logging.getLogger(__name__)


class Intent(Enum):
    LOOKUP = "RETAS_LOOKUP"
    COUNT = "RETAS_COUNT"
    MAX = "RETAS_MAX"
    MIN = "RETAS_MIN"
    SUM = "RETAS_SUM"
    AVG = "RETAS_AVG"
    LLM_COMPOUND = "LLM_COMPOUND"
    LLM_COMPARE = "LLM_COMPARE"
    LLM_ANALYSIS = "LLM_ANALYSIS"
    LLM_FILTER = "LLM_FILTER"
    LLM_GROUP = "LLM_GROUP"
    NONE = "NONE"

    def is_retas(self) -> bool:
        return self.name in {
            "LOOKUP", "COUNT", "MAX", "MIN", "SUM", "AVG",
        }

    def is_llm(self) -> bool:
        return self.name in {
            "LLM_COMPOUND", "LLM_COMPARE",
            "LLM_FILTER", "LLM_GROUP",
        }


# ── Stopword set ─────────────────────────────────────────────────
_STOPWORDS: frozenset[str] = frozenset({
    'cho', 'tôi', 'bạn', 'em', 'chị', 'thầy',
    'về', 'của', 'và', 'các', 'có', 'là', 'không', 'gì',
    'nào', 'thế', 'này', 'một', 'những', 'được', 'với',
    'hoặc', 'hay', 'ra', 'lên', 'xuống', 'qua', 'lại',
    'khi', 'đã', 'đang', 'sẽ', 'số', 'mấy', 'nhiêu', 'bao',
    'biết', 'xin', 'hãy', 'hỏi', 'giúp', 'ơn', 'ạ', 'à',
    'thì', 'mà', 'là', 'ở', 'tại', 'trong', 'ngoài', 'trên',
    'dưới', 'cả', 'rất', 'lắm', 'quá', 'nữa', 'vẫn', 'cứ',
    'lớp', 'môn', 'học', 'phần', 'dạy', 'dành', 'sinh', 'viên',
    'file', 'tệp', 'thời', 'khóa', 'biểu', 'thoi', 'khoa', 'bieu',
})


# ── Intent patterns ──────────────────────────────────────────────
_INTENT_PATTERNS: list[tuple[re.Pattern, Intent]] = [
    # RETAS
    (re.compile(r'(tổng|cộng)\s+(của|số)?', re.I), Intent.SUM),
    (re.compile(r'trung\s*bình', re.I), Intent.AVG),
    (re.compile(r'(cao|nhiều|lớn|dài|rộng|nặng|sâu).{0,6}(nhất)', re.I), Intent.MAX),
    (re.compile(r'(thấp|ít|ngắn|hẹp|nhẹ|nhỏ|nông|cạn).{0,6}(nhất)', re.I), Intent.MIN),
    (re.compile(r'(bao.?nhiêu|mấy|đếm|số.?lượng|có\s.*không)', re.I), Intent.COUNT),

    # LLM
    (re.compile(r'(vừa|đồng.?thời|cả).{1,40}(vừa|cả|mà)', re.I), Intent.LLM_COMPOUND),
    (re.compile(r'(so.?sánh|khác.?nhau|chênh.?lệch|nhiều.?hơn|ít.?hơn)', re.I), Intent.LLM_COMPARE),
    (re.compile(r'(phân.?tích|tổng.?quan|thống.?kê|lên.?kế.?hoạch|tạo.*plan)', re.I), Intent.LLM_ANALYSIS),
    (re.compile(r'(điều.?kiện|lọc|filter|trong.?đó)', re.I), Intent.LLM_FILTER),
    (re.compile(r'(group|nhóm|phân.?loại|chia.?loại|theo.?từng)', re.I), Intent.LLM_GROUP),
]


# ── Keyword extraction ────────────────────────────────────────────
_SINGLE_DIGIT = re.compile(r'^\d{1,2}$')
_DATE_FORMATS = (
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%y",
    "%d-%m-%y",
)


def _extract_keywords(question: str) -> list[str]:
    tokens = re.findall(r'[A-Za-z0-9\u00C0-\u1EF9]+', question.lower())
    keywords = []
    for t in tokens:
        if t in _STOPWORDS:
            continue
        if _SINGLE_DIGIT.match(t):
            continue
        keywords.append(t)
    return keywords


def _select_search_keywords(keywords: list[str]) -> list[str]:
    code_like = [
        kw for kw in keywords
        if re.search(r'[a-zA-Z]', kw) and re.search(r'\d', kw)
    ]
    if code_like:
        return code_like
    return keywords


def _sql_quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _like_pattern(value: str) -> str:
    escaped = str(value).replace("'", "''")
    return f"'%{escaped}%'"


def _contains_expr(expr: str, value: str) -> str:
    return f"LOWER(CAST({expr} AS TEXT)) LIKE LOWER({_like_pattern(value)})"


def _search_text_conditions(keywords: list[str]) -> str:
    return " AND ".join(_contains_expr("search_text", kw) for kw in keywords)


def _schema_with_profiles(schema: list[dict], sample_data: str | None = None) -> list[dict]:
    try:
        samples = json.loads(sample_data or "[]")
    except (json.JSONDecodeError, TypeError):
        samples = []

    profiled: list[dict] = []
    for col in schema:
        name = col.get("name", "")
        values = [row.get(name) for row in samples if isinstance(row, dict)]
        inferred = build_column_profile(
            original_name=col.get("original_name", name),
            safe_name=name,
            dtype=col.get("dtype", "TEXT"),
            values=values,
        )
        if col.get("semantic_type"):
            name_compact = compact_text(f"{col.get('original_name', '')} {col.get('name', '')}")
            if (
                col.get("semantic_type") == "birth_year"
                and col.get("dtype") not in {"INTEGER", "REAL"}
                and ("sinh" in name_compact or "birth" in name_compact)
            ):
                upgraded = dict(col)
                upgraded["semantic_type"] = "date_of_birth"
                upgraded["semantic_confidence"] = max(float(upgraded.get("semantic_confidence") or 0.0), 0.9)
                profiled.append(upgraded)
                continue
            if (
                col.get("semantic_type") in {"generic_text", "generic_number"}
                and inferred.get("semantic_type") not in {"generic_text", "generic_number"}
            ):
                profiled.append({**col, **inferred})
                continue
            profiled.append(col)
            continue
        profiled.append(inferred)
    return profiled


def _column_text(col: dict) -> str:
    parts = [
        col.get("name", ""),
        col.get("original_name", ""),
        col.get("semantic_type", ""),
        " ".join(col.get("aliases") or []),
        " ".join(str(v) for v in (col.get("sample_values") or [])[:5]),
    ]
    return normalize_text(" ".join(parts))


def _semantic_columns(schema: list[dict], semantic_types: set[str]) -> list[dict]:
    return [c for c in schema if c.get("semantic_type") in semantic_types]


def _score_column(col: dict, question: str, semantic_types: set[str] | None = None) -> int:
    score = 0
    q_norm = normalize_text(question)
    q_compact = compact_text(question)
    col_name = normalize_text(col.get("original_name") or col.get("name") or "")
    col_compact = compact_text(col.get("original_name") or col.get("name") or "")
    col_text = _column_text(col)

    if semantic_types and col.get("semantic_type") in semantic_types:
        score += int(float(col.get("semantic_confidence") or 0.5) * 100)
    if col_name and (col_name in q_norm or col_compact in q_compact):
        score += 80
    for alias in col.get("aliases") or []:
        alias_norm = normalize_text(alias)
        if alias_norm and alias_norm in q_norm:
            score += 50
    for token in q_norm.split():
        if len(token) >= 3 and token in col_text:
            score += 8
    return score


def _best_column(
    schema: list[dict],
    question: str,
    semantic_types: set[str],
    *,
    require_numeric: bool = False,
    min_score: int = 60,
) -> dict | None:
    candidates = [
        col for col in schema
        if not require_numeric or col.get("dtype") in ("INTEGER", "REAL")
    ]
    ranked = sorted(
        ((col, _score_column(col, question, semantic_types)) for col in candidates),
        key=lambda item: item[1],
        reverse=True,
    )
    if not ranked or ranked[0][1] < min_score:
        return None
    return ranked[0][0]


def _parse_date_value(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    text_value = str(value).strip()
    if not text_value:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text_value[:10], fmt)
        except ValueError:
            continue
    return None


def _to_float(value: Any) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _extract_lookup_entity(text_value: str) -> str | None:
    patterns = [
        r"(?:thông\s*tin\s*về|biết\s*về|nói\s*về|về)\s+(.+)$",
        r"(?:thong\s*tin\s*ve|biet\s*ve|noi\s*ve|ve)\s+(.+)$",
    ]
    entity = None
    for pattern in patterns:
        match = re.search(pattern, text_value, flags=re.I)
        if match:
            entity = match.group(1)
            break
    if entity is None:
        return None
    entity = re.split(r"\b(?:và|va|đồng thời|dong thoi|còn|con|ai là|ai la|có bao nhiêu|co bao nhieu)\b", entity, maxsplit=1, flags=re.I)[0]
    return entity.strip() or None


def _extract_compare_entities(question: str) -> list[str]:
    match = re.search(r"(?:so\s*sánh|so\s*sanh)\s+(.+)$", question, flags=re.I)
    if not match:
        return []
    tail = match.group(1)
    parts = [p.strip() for p in re.split(r"\s+(?:và|va|với|voi)\s+", tail, flags=re.I) if p.strip()]
    return parts[:4]


def _filter_keywords_for_question(question: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9\u00C0-\u1EF9]+", question.lower())
    blocked = _STOPWORDS.union({
        "ai", "người", "nguoi", "nào", "nao", "lớn", "lon", "tuổi", "tuoi",
        "cao", "già", "gia", "nhỏ", "nho", "trẻ", "tre", "ít", "it",
        "nhất", "nhat", "danh", "sách", "sach",
        "thông", "tin", "thong", "so", "sánh", "sanh", "tổng", "tong",
        "trung", "bình", "binh", "cao", "thấp", "thap",
    })
    result = []
    for token in tokens:
        if token in blocked:
            continue
        if _SINGLE_DIGIT.match(token):
            continue
        result.append(token)
    return result


def _asks_gender_count(text_value: str) -> bool:
    norm = normalize_text(text_value)
    if "bao nhieu" not in norm and "so luong" not in norm and "dem" not in norm:
        return False
    has_female = bool(re.search(r"\b(?:nu|female)\b", norm))
    has_male = bool(re.search(r"\b(?:nam|male)\b", norm))
    return has_male and has_female


def _fuzzy_score(left: str, right: str) -> float:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm in right_norm or right_norm in left_norm:
        return 1.0
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def _has_code_like_token(keywords: list[str]) -> bool:
    return any(re.search(r"[a-zA-Z]", kw) and re.search(r"\d", kw) for kw in keywords)


@dataclass
class PlannedTask:
    kind: str
    text: str
    entity: str | None = None
    entities: list[str] | None = None
    target_hint: str | None = None
    group_by_hint: str | None = None
    value_hints: list[str] | None = None
    metric_hint: str | None = None
    direction: str | None = None
    op: str | None = None
    filters: list[dict[str, Any]] | None = None


_LLM_TASK_TYPES = {
    "lookup",
    "lookup_entity",
    "count",
    "count_rows",
    "group_count",
    "aggregate",
    "extreme",
    "compare",
}
_LLM_AGG_OPS = {"sum", "avg", "min", "max", "count"}
_LLM_FILTER_OPS = {"contains", "equals", "gt", "lt", "gte", "lte", "between"}


def _extract_json_object(value: str) -> dict[str, Any] | None:
    text_value = (value or "").strip()
    if text_value.startswith("```"):
        text_value = re.sub(r"^```(?:json)?\s*", "", text_value, flags=re.I)
        text_value = re.sub(r"\s*```$", "", text_value)
    start = text_value.find("{")
    end = text_value.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        parsed = json.loads(text_value[start:end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _coerce_text_list(value: Any, *, limit: int = 6) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if item is None:
            continue
        text_item = str(item).strip()
        if text_item:
            result.append(text_item[:120])
        if len(result) >= limit:
            break
    return result


def _sanitize_filters(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    filters: list[dict[str, Any]] = []
    for item in value[:6]:
        if not isinstance(item, dict):
            continue
        op = str(item.get("op") or "contains").strip().lower()
        if op not in _LLM_FILTER_OPS:
            continue
        field_hint = str(item.get("field_hint") or item.get("field") or "").strip()[:120]
        raw_value = item.get("value")
        if raw_value is None:
            continue
        filters.append({"field_hint": field_hint, "op": op, "value": str(raw_value).strip()[:200]})
    return filters


def _task_from_llm(raw_task: dict[str, Any], question: str) -> PlannedTask | None:
    task_type = str(raw_task.get("type") or "").strip().lower()
    if task_type not in _LLM_TASK_TYPES:
        return None

    if task_type in {"lookup", "lookup_entity"}:
        entity = str(raw_task.get("entity") or "").strip()
        if not entity:
            return None
        return PlannedTask(
            "lookup",
            question,
            entity=entity[:200],
            target_hint=str(raw_task.get("target_hint") or raw_task.get("entity_type") or "").strip()[:80] or None,
        )

    if task_type == "compare":
        entities = _coerce_text_list(raw_task.get("entities"), limit=4)
        if not entities:
            return None
        return PlannedTask(
            "compare",
            question,
            entities=entities,
            metric_hint=str(raw_task.get("metric_hint") or "").strip()[:120] or None,
        )

    if task_type in {"count", "count_rows"}:
        return PlannedTask("count", question, filters=_sanitize_filters(raw_task.get("filters")))

    if task_type == "group_count":
        group_by_hint = str(raw_task.get("group_by_hint") or raw_task.get("dimension") or "").strip()
        if not group_by_hint:
            return None
        return PlannedTask(
            "group_count",
            question,
            group_by_hint=group_by_hint[:120],
            value_hints=_coerce_text_list(raw_task.get("value_hints"), limit=10),
            filters=_sanitize_filters(raw_task.get("filters")),
        )

    if task_type == "aggregate":
        op = str(raw_task.get("op") or "").strip().lower()
        if op not in _LLM_AGG_OPS:
            return None
        metric_hint = str(raw_task.get("metric_hint") or raw_task.get("metric") or "").strip()
        if not metric_hint:
            return None
        return PlannedTask(
            "aggregate",
            question,
            op=op,
            metric_hint=metric_hint[:120],
            filters=_sanitize_filters(raw_task.get("filters")),
        )

    if task_type == "extreme":
        direction = str(raw_task.get("direction") or "").strip().lower()
        if direction not in {"max", "min"}:
            return None
        metric_hint = str(raw_task.get("metric_hint") or raw_task.get("metric") or "").strip()
        if not metric_hint:
            return None
        return PlannedTask(
            "extreme",
            question,
            direction=direction,
            metric_hint=metric_hint[:120],
            target_hint=str(raw_task.get("target_hint") or "").strip()[:80] or None,
            filters=_sanitize_filters(raw_task.get("filters")),
        )

    return None


def _tasks_from_llm_plan(plan: dict[str, Any], question: str) -> list[PlannedTask]:
    raw_tasks = plan.get("tasks")
    if not isinstance(raw_tasks, list):
        return []
    tasks: list[PlannedTask] = []
    for raw_task in raw_tasks[:5]:
        if not isinstance(raw_task, dict):
            continue
        task = _task_from_llm(raw_task, question)
        if task is not None:
            tasks.append(task)
    return tasks


# ── Intent classification ─────────────────────────────────────────
def _classify_intent(question: str, keywords: list[str]) -> Intent:
    for pattern, intent in _INTENT_PATTERNS:
        if pattern.search(question):
            logger.debug("intent=%s matched by %s", intent.value, pattern.pattern)
            return intent
    if keywords:
        return Intent.LOOKUP
    return Intent.NONE


# ── Column resolver ───────────────────────────────────────────────
def _resolve_column(question: str, schema: list[dict]) -> list[str] | None:
    numeric = [c['name'] for c in schema if c['dtype'] in ('INTEGER', 'REAL')]
    if not numeric:
        return None

    q_words = {w.lower() for w in re.findall(r'[a-zA-Z0-9_\u00C0-\u1EF9]+', question)}
    matched: list[str] = []

    for col in numeric:
        col_norm = col.lower().replace('_', '')
        for qw in q_words:
            if qw in col_norm or (len(qw) >= 3 and col_norm in qw):
                matched.append(col)
                break

    return matched[:3] if matched else None


# ── Post-processor ────────────────────────────────────────────────
_FORBIDDEN = re.compile(r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE|EXEC)\b', re.I)


class SqlFixer:
    """Validate and fix LLM-generated SQL against actual schema."""

    def __init__(self, schema: list[dict]) -> None:
        self._col_map: dict[str, str] = {}
        for c in schema:
            key = c['name'].lower().replace('_', '')
            self._col_map[key] = c['name']
        self._col_map['search_text'] = 'search_text'
        self._col_map['row_idx'] = '_row_idx'

    def fix(self, sql: str) -> str:
        sql = self._fix_columns(sql)
        sql = self._fix_like(sql)
        sql = self._fix_limit(sql)
        sql = self._validate(sql)
        return sql

    def _fix_columns(self, sql: str) -> str:
        placeholders: dict[str, str] = {}
        seq = 0

        def _protect(m: re.Match) -> str:
            nonlocal seq
            ph = f'__STR_{seq}__'
            seq += 1
            placeholders[ph] = m.group(0)
            return ph

        sql = re.sub(r"'[^']*'", _protect, sql)

        def _replace(m: re.Match) -> str:
            col = m.group(1)
            key = col.lower().replace('_', '')
            if key in self._col_map:
                return f'"{self._col_map[key]}"'
            return m.group(0)
        sql = re.sub(r'"([^"]+)"', _replace, sql)

        for key, actual in self._col_map.items():
            pattern = re.compile(rf'(?<!"){re.escape(key)}(?!")', re.I)
            sql = pattern.sub(f'"{actual}"', sql)

        for ph, original in placeholders.items():
            sql = sql.replace(ph, original)

        return sql

    def _fix_like(self, sql: str) -> str:
        return re.sub(r'\bLIKE\b', 'ILIKE', sql, flags=re.I)

    def _fix_limit(self, sql: str) -> str:
        if 'LIMIT' not in sql.upper():
            if not re.search(r'\b(COUNT|SUM|MAX|MIN|AVG)\s*\(', sql, re.I):
                sql += f' LIMIT {SQL_MAX_ROWS}'
        return sql

    def _validate(self, sql: str) -> str:
        if _FORBIDDEN.search(sql):
            raise ValueError("Forbidden SQL operation")
        if not re.match(r'^\s*SELECT\b', sql, re.I):
            raise ValueError("Only SELECT allowed")
        return sql


# ── Main service ──────────────────────────────────────────────────
MAX_QUERY_CHARS: int = 5000


class ExcelQueryService:
    def __init__(self) -> None:
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            from rag_core.common.llm import build_chat_llm
            self._llm = build_chat_llm()
        return self._llm

    # ── Table resolution ─────────────────────────────────────────
    def get_tables(self, db: Session, user_id: str) -> list[ExcelTableRecord]:
        records = db.query(ExcelTableRecord).filter(
            ExcelTableRecord.user_id == user_id
        ).all()
        logger.info("get_tables: user_id=%s found %d tables via direct query", user_id, len(records))
        if records:
            return records
        try:
            from ..models import DocumentRecord
            user_id_int = int(user_id) if user_id.isdigit() else None
            if user_id_int is not None:
                doc_ids = [
                    r[0] for r in db.query(DocumentRecord.id)
                    .filter(DocumentRecord.owner_id == user_id_int)
                    .all()
                ]
                if doc_ids:
                    records = (
                        db.query(ExcelTableRecord)
                        .filter(ExcelTableRecord.document_id.in_(doc_ids))
                        .all()
                    )
                    logger.info("get_tables: user_id=%s (as int=%d) found %d documents, %d excel tables via fallback", user_id, user_id_int, len(doc_ids), len(records))
        except Exception:
            pass
        return records

    # ── Main entry ────────────────────────────────────────────────
    def query(self, db: Session, user_id: str, question: str) -> str | None:
        tables = self.get_tables(db, user_id)
        if not tables:
            logger.info("excel_query: no tables found for user_id=%s", user_id)
            return None

        keywords = _extract_keywords(question)
        intent = _classify_intent(question, keywords)
        logger.info("excel_query: user_id=%s question='%s' keywords=%s intent=%s", user_id, question[:100], keywords, intent.value)

        # Intent NONE + no keywords → can't help
        if intent == Intent.NONE:
            logger.info("excel_query: intent=NONE with no keywords, returning None")
            return None

        # ANALYSIS is handled first (Python multi-query, returns immediately)
        if intent == Intent.LLM_ANALYSIS:
            logger.info("excel_query: running analysis for %d tables", len(tables))
            return self._run_analysis(tables, db)

        # Try each table
        for i, table in enumerate(tables):
            result = self._query_table(table, db, intent, keywords, question)
            if result is not None:
                logger.info("excel_query: found result in table %d/%d (%s)", i+1, len(tables), table.table_name)
                return result

        logger.info("excel_query: no result found in any of %d tables", len(tables))
        return None

    def _query_table(
        self,
        table: ExcelTableRecord,
        db: Session,
        intent: Intent,
        keywords: list[str],
        question: str,
    ) -> str | None:
        schema_list = _schema_with_profiles(json.loads(table.column_schema), table.sample_data)

        try:
            planned_result = self._query_planned(table, db, question, schema_list)
            if planned_result is not None:
                return planned_result

            if intent.is_retas():
                result = self._query_retas(
                    table, db, intent, keywords, question, schema_list
                )
                if result and "Không có kết quả phù hợp" not in result and not (intent == Intent.COUNT and "\n| 0 |" in result):
                    return result
                return None
                
            if intent.is_llm():
                llm_result = self._query_llm(table, db, question, schema_list)
                if llm_result and "Không có kết quả phù hợp" not in llm_result:
                    return llm_result
                return None

            # Intent.LOOKUP (fallback when no pattern matched)
            result = self._query_retas(
                table, db, Intent.LOOKUP, keywords, question, schema_list
            )
            if result and "Không có kết quả phù hợp" not in result:
                return result
            llm_result = self._query_llm(table, db, question, schema_list)
            if llm_result and "Không có kết quả phù hợp" not in llm_result:
                return llm_result
            return None
        except Exception as exc:
            logger.debug("table_query_failed: %s — %s", table.table_name, exc)
            return None

    # ── LLM planner + deterministic executor ────────────────────
    def _schema_summary_for_planner(self, table: ExcelTableRecord, schema_list: list[dict]) -> dict[str, Any]:
        columns: list[dict[str, Any]] = []
        for col in schema_list[:60]:
            columns.append({
                "name": col.get("name"),
                "original_name": col.get("original_name") or col.get("name"),
                "dtype": col.get("dtype"),
                "semantic_type": col.get("semantic_type"),
                "sample_values": (col.get("sample_values") or [])[:8],
            })
        return {
            "table_name": table.table_name,
            "sheet_name": table.sheet_name,
            "row_count": table.row_count,
            "columns": columns,
        }

    def _build_planner_prompt(self, table: ExcelTableRecord, question: str, schema_list: list[dict]) -> str:
        schema_summary = self._schema_summary_for_planner(table, schema_list)
        return (
            "Bạn là Excel query planner cho dữ liệu bảng. "
            "Nhiệm vụ của bạn là chuyển câu hỏi tiếng Việt/tự nhiên thành JSON plan.\n\n"
            "QUY TẮC BẮT BUỘC:\n"
            "- Chỉ trả JSON hợp lệ, không markdown, không giải thích.\n"
            "- Không viết SQL.\n"
            "- Không bịa tên cột. Dùng hint ngôn ngữ tự nhiên như group_by_hint, metric_hint, field_hint.\n"
            "- Nếu câu hỏi có nhiều ý, tách thành nhiều tasks theo đúng thứ tự.\n"
            "- Chỉ dùng task type: lookup, count, group_count, aggregate, extreme, compare.\n"
            "- aggregate.op chỉ được là sum, avg, min, max, count.\n"
            "- filter.op chỉ được là contains, equals, gt, lt, gte, lte, between.\n"
            "- Với câu hỏi thống kê theo nhóm như nam/nữ, con trai/con gái, trạng thái, học vị, nơi sinh, "
            "hãy dùng group_count với group_by_hint là khái niệm cần nhóm.\n"
            "- Với câu hỏi người lớn tuổi/nhỏ tuổi nhất, dùng extreme metric_hint='tuổi hoặc ngày sinh', "
            "direction=max cho lớn tuổi nhất và direction=min cho nhỏ tuổi nhất.\n\n"
            "JSON schema mong muốn:\n"
            "{\n"
            '  "tasks": [\n'
            '    {"type":"lookup","entity":"...","target_hint":"person|course|product|row|unknown"},\n'
            '    {"type":"count","filters":[{"field_hint":"...","op":"contains","value":"..."}]},\n'
            '    {"type":"group_count","group_by_hint":"...","value_hints":["..."],"filters":[]},\n'
            '    {"type":"aggregate","op":"sum|avg|min|max|count","metric_hint":"...","filters":[]},\n'
            '    {"type":"extreme","direction":"max|min","metric_hint":"...","target_hint":"row|person|unknown","filters":[]},\n'
            '    {"type":"compare","entities":["..."],"metric_hint":"..."}\n'
            "  ]\n"
            "}\n\n"
            f"SCHEMA SUMMARY:\n{json.dumps(schema_summary, ensure_ascii=False)}\n\n"
            f"USER QUESTION:\n{question}\n"
        )

    def _plan_tasks_with_llm(
        self,
        table: ExcelTableRecord,
        question: str,
        schema_list: list[dict],
    ) -> list[PlannedTask]:
        try:
            response = self.llm.invoke(self._build_planner_prompt(table, question, schema_list))
            raw = getattr(response, "content", str(response))
            plan = _extract_json_object(raw)
            if plan is None:
                logger.warning("excel_llm_planner_invalid_json")
                return []
            tasks = _tasks_from_llm_plan(plan, question)
            if tasks:
                logger.info("excel_llm_planner_tasks: %s", ",".join(task.kind for task in tasks))
            return tasks
        except Exception as exc:
            logger.warning("excel_llm_planner_failed: %s", str(exc)[:200])
            return []

    def _plan_tasks(self, table: ExcelTableRecord, question: str, schema_list: list[dict]) -> list[PlannedTask]:
        llm_tasks = self._plan_tasks_with_llm(table, question, schema_list)
        if llm_tasks:
            return llm_tasks
        return self._plan_tasks_rule(question)

    def _plan_tasks_rule(self, question: str) -> list[PlannedTask]:
        norm = normalize_text(question)
        raw_parts = [
            part.strip()
            for part in re.split(r"\s+(?:và|va|đồng thời|dong thoi)\s+", question)
            if part.strip()
        ] or [question]

        tasks: list[PlannedTask] = []
        if "so sanh" in norm:
            entities = _extract_compare_entities(question)
            if entities:
                tasks.append(PlannedTask("compare", question, entities=entities))
                return tasks

        has_gender_count = _asks_gender_count(question)

        for part in raw_parts:
            part_norm = normalize_text(part)
            entity = _extract_lookup_entity(part)
            if entity:
                tasks.append(PlannedTask("lookup", part, entity=entity))
                continue
            if re.search(r"\b(?:lon tuoi nhat|cao tuoi nhat|gia nhat)\b", part_norm):
                tasks.append(PlannedTask("oldest", part))
                continue
            if re.search(r"\b(?:nho tuoi nhat|it tuoi nhat|tre nhat)\b", part_norm):
                tasks.append(PlannedTask("youngest", part))
                continue
            if has_gender_count and re.search(r"\b(?:nam|nu|male|female)\b", part_norm):
                continue
            if re.search(r"\b(?:bao nhieu|so luong|dem|may)\b", part_norm):
                tasks.append(PlannedTask("count", part))
                continue
            if re.search(r"\b(?:tong|cong)\b", part_norm):
                tasks.append(PlannedTask("sum", part))
                continue
            if "trung binh" in part_norm:
                tasks.append(PlannedTask("avg", part))
                continue
            if re.search(r"\b(?:cao nhat|lon nhat|nhieu nhat)\b", part_norm):
                tasks.append(PlannedTask("max", part))
                continue
            if re.search(r"\b(?:thap nhat|it nhat|nho nhat)\b", part_norm):
                tasks.append(PlannedTask("min", part))
                continue
        if has_gender_count:
            tasks.append(PlannedTask("gender_count", question))
        return tasks

    def _query_planned(
        self,
        table: ExcelTableRecord,
        db: Session,
        question: str,
        schema_list: list[dict],
    ) -> str | None:
        tasks = self._plan_tasks(table, question, schema_list)
        if not tasks:
            return None

        parts: list[str] = []
        for task in tasks:
            result = self._run_planned_task(table, db, task, schema_list)
            if result:
                parts.append(f"{self._planned_task_title(task)}\n{result}")

        if not parts:
            return None
        if len(parts) == 1:
            return parts[0]
        return "\n\n".join(parts)

    def _planned_task_title(self, task: PlannedTask) -> str:
        if task.kind == "lookup" and task.entity:
            return f"Thông tin về {task.entity}:"
        if task.kind == "compare":
            return "Kết quả so sánh:"
        if task.kind == "oldest":
            return "Người lớn tuổi nhất phù hợp điều kiện:"
        if task.kind == "youngest":
            return "Người nhỏ tuổi nhất phù hợp điều kiện:"
        if task.kind == "group_count":
            hint = task.group_by_hint or "nhóm"
            return f"Thống kê theo {hint}:"
        if task.kind == "aggregate":
            return "Kết quả tính toán:"
        if task.kind == "extreme":
            return "Kết quả tìm giá trị phù hợp:"
        labels = {
            "count": "Kết quả đếm:",
            "gender_count": "Thống kê giới tính:",
            "sum": "Kết quả tính tổng:",
            "avg": "Kết quả trung bình:",
            "max": "Giá trị cao nhất:",
            "min": "Giá trị thấp nhất:",
        }
        return labels.get(task.kind, "Kết quả:")

    def _run_planned_task(
        self,
        table: ExcelTableRecord,
        db: Session,
        task: PlannedTask,
        schema_list: list[dict],
    ) -> str | None:
        if task.kind == "lookup":
            return self._query_lookup_entity(table, db, schema_list, task.entity or task.text)
        if task.kind == "compare":
            parts = [
                self._query_lookup_entity(table, db, schema_list, entity)
                for entity in (task.entities or [])
            ]
            parts = [part for part in parts if part]
            return "\n\n".join(parts) if parts else None
        if task.kind == "oldest":
            return self._query_oldest_person(table, db, schema_list, task.text)
        if task.kind == "youngest":
            return self._query_youngest_person(table, db, schema_list, task.text)
        if task.kind == "gender_count":
            return self._query_gender_count(table, db, schema_list)
        if task.kind == "group_count":
            return self._query_group_count(table, db, schema_list, task)
        if task.kind == "aggregate":
            return self._query_generic_aggregate(table, db, schema_list, task)
        if task.kind == "extreme":
            return self._query_generic_extreme(table, db, schema_list, task)
        if task.kind in {"count", "sum", "avg", "max", "min"}:
            return self._query_basic_aggregate(table, db, schema_list, task)
        return None

    def _query_lookup_entity(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        entity: str,
    ) -> str | None:
        entity = entity.strip()
        if not entity:
            return None

        person_col = _best_column(schema_list, entity, {"person_name"}, min_score=65)
        conditions = []
        if person_col is not None:
            conditions.append(_contains_expr(_sql_quote_identifier(person_col["name"]), entity))
        conditions.append(_contains_expr("search_text", entity))
        sql = (
            f'SELECT * FROM "{table.table_name}" '
            f'WHERE {" OR ".join(conditions)} '
            f'ORDER BY "_row_idx" LIMIT {SQL_MAX_ROWS}'
        )
        result = self._execute(sql, db)
        if not result or not result[0]:
            fuzzy_result = self._query_lookup_entity_fuzzy(table, db, schema_list, entity, person_col)
            if fuzzy_result is not None:
                return fuzzy_result
            return None
        return self._format_result(result)

    def _query_lookup_entity_fuzzy(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        entity: str,
        person_col: dict | None,
    ) -> str | None:
        person_col = person_col or _best_column(schema_list, entity, {"person_name"}, min_score=45)
        if person_col is None:
            return None
        sql = (
            f'SELECT * FROM "{table.table_name}" '
            f'WHERE {_sql_quote_identifier(person_col["name"])} IS NOT NULL '
            f'ORDER BY "_row_idx" LIMIT {SQL_MAX_ROWS}'
        )
        result = self._execute(sql, db)
        if not result or not result[0]:
            return None
        rows, col_keys = result
        col_index = col_keys.index(person_col["name"])
        ranked = [
            (row, _fuzzy_score(entity, row[col_index]))
            for row in rows
            if row[col_index] is not None
        ]
        ranked.sort(key=lambda item: item[1], reverse=True)
        if not ranked or ranked[0][1] < 0.82:
            return None
        return self._format_result(([ranked[0][0]], col_keys))

    def _query_oldest_person(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        question: str,
    ) -> str | None:
        name_col = _best_column(schema_list, question, {"person_name"}, min_score=45)
        age_col = _best_column(schema_list, question, {"age"}, require_numeric=True, min_score=60)
        birth_year_col = _best_column(schema_list, question, {"birth_year"}, min_score=60)
        dob_col = _best_column(schema_list, question, {"date_of_birth"}, min_score=60)

        if name_col is None:
            name_candidates = _semantic_columns(schema_list, {"person_name"})
            name_col = name_candidates[0] if name_candidates else None

        filter_terms = _filter_keywords_for_question(question)
        where_clause = ""
        if filter_terms:
            where_clause = "WHERE " + _search_text_conditions(filter_terms)

        if age_col is not None:
            sql = (
                f'SELECT * FROM "{table.table_name}" {where_clause} '
                f'ORDER BY {_sql_quote_identifier(age_col["name"])} IS NULL ASC, '
                f'{_sql_quote_identifier(age_col["name"])} DESC LIMIT 1'
            )
            result = self._execute(sql, db)
            if result and result[0]:
                return self._format_result(result)

        if birth_year_col is not None and birth_year_col.get("dtype") in {"INTEGER", "REAL"}:
            sql = (
                f'SELECT * FROM "{table.table_name}" {where_clause} '
                f'ORDER BY {_sql_quote_identifier(birth_year_col["name"])} IS NULL ASC, '
                f'{_sql_quote_identifier(birth_year_col["name"])} ASC LIMIT 1'
            )
            result = self._execute(sql, db)
            if result and result[0]:
                return self._format_result(result)

        date_like_col = dob_col or birth_year_col
        if date_like_col is None:
            logger.info("excel_query_oldest: no age/date/year column resolved for table=%s", table.table_name)
            return None

        sql = (
            f'SELECT * FROM "{table.table_name}" {where_clause} '
            f'ORDER BY "_row_idx" LIMIT {SQL_MAX_ROWS}'
        )
        result = self._execute(sql, db)
        if not result or not result[0]:
            return None
        rows, col_keys = result
        col_index = col_keys.index(date_like_col["name"])
        selected = None
        selected_key = None
        for row in rows:
            value = row[col_index]
            if date_like_col.get("semantic_type") == "birth_year":
                key = _to_float(value)
                if key is None:
                    continue
            else:
                parsed = _parse_date_value(value)
                if parsed is None:
                    continue
                key = parsed.timestamp()
            if selected is None or key < selected_key:
                selected = row
                selected_key = key

        if selected is None:
            return None
        return self._format_result(([selected], col_keys))

    def _query_youngest_person(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        question: str,
    ) -> str | None:
        name_col = _best_column(schema_list, question, {"person_name"}, min_score=45)
        age_col = _best_column(schema_list, question, {"age"}, require_numeric=True, min_score=60)
        birth_year_col = _best_column(schema_list, question, {"birth_year"}, min_score=60)
        dob_col = _best_column(schema_list, question, {"date_of_birth"}, min_score=60)

        if name_col is None:
            name_candidates = _semantic_columns(schema_list, {"person_name"})
            name_col = name_candidates[0] if name_candidates else None

        filter_terms = _filter_keywords_for_question(question)
        where_clause = ""
        if filter_terms:
            where_clause = "WHERE " + _search_text_conditions(filter_terms)

        if age_col is not None:
            sql = (
                f'SELECT * FROM "{table.table_name}" {where_clause} '
                f'ORDER BY {_sql_quote_identifier(age_col["name"])} IS NULL ASC, '
                f'{_sql_quote_identifier(age_col["name"])} ASC LIMIT 1'
            )
            result = self._execute(sql, db)
            if result and result[0]:
                return self._format_result(result)

        if birth_year_col is not None and birth_year_col.get("dtype") in {"INTEGER", "REAL"}:
            sql = (
                f'SELECT * FROM "{table.table_name}" {where_clause} '
                f'ORDER BY {_sql_quote_identifier(birth_year_col["name"])} IS NULL ASC, '
                f'{_sql_quote_identifier(birth_year_col["name"])} DESC LIMIT 1'
            )
            result = self._execute(sql, db)
            if result and result[0]:
                return self._format_result(result)

        date_like_col = dob_col or birth_year_col
        if date_like_col is None:
            logger.info("excel_query_youngest: no age/date/year column resolved for table=%s", table.table_name)
            return None

        sql = (
            f'SELECT * FROM "{table.table_name}" {where_clause} '
            f'ORDER BY "_row_idx" LIMIT {SQL_MAX_ROWS}'
        )
        result = self._execute(sql, db)
        if not result or not result[0]:
            return None
        rows, col_keys = result
        col_index = col_keys.index(date_like_col["name"])
        selected = None
        selected_key = None
        for row in rows:
            value = row[col_index]
            if date_like_col.get("semantic_type") == "birth_year":
                key = _to_float(value)
                if key is None:
                    continue
            else:
                parsed = _parse_date_value(value)
                if parsed is None:
                    continue
                key = parsed.timestamp()
            if selected is None or key > selected_key:
                selected = row
                selected_key = key

        if selected is None:
            return None
        return self._format_result(([selected], col_keys))

    def _resolve_hint_column(
        self,
        schema_list: list[dict],
        hint: str | None,
        *,
        require_numeric: bool = False,
        min_score: int = 45,
    ) -> dict | None:
        hint = (hint or "").strip()
        if not hint:
            return None
        candidates = [
            col for col in schema_list
            if not require_numeric or col.get("dtype") in ("INTEGER", "REAL")
        ]
        ranked = sorted(
            ((col, _score_column(col, hint, None)) for col in candidates),
            key=lambda item: item[1],
            reverse=True,
        )
        if ranked and ranked[0][1] >= min_score:
            return ranked[0][0]

        hint_norm = normalize_text(hint)
        for semantic in {
            "gender", "degree", "education_level", "department", "course_code",
            "course_name", "class_name", "credit", "quantity", "age",
            "date_of_birth", "birth_year", "person_name", "teacher",
        }:
            semantic_text = normalize_text(" ".join([semantic, *([])]))
            if semantic_text and semantic_text in hint_norm:
                col = _best_column(schema_list, hint, {semantic}, require_numeric=require_numeric, min_score=50)
                if col is not None:
                    return col
        return None

    def _where_clause_for_filters(self, schema_list: list[dict], filters: list[dict[str, Any]] | None) -> str:
        conditions: list[str] = []
        for filter_item in filters or []:
            value = str(filter_item.get("value") or "").strip()
            if not value:
                continue
            col = self._resolve_hint_column(schema_list, filter_item.get("field_hint"), min_score=45)
            expr = _sql_quote_identifier(col["name"]) if col is not None else "search_text"
            op = filter_item.get("op") or "contains"
            if op == "contains":
                conditions.append(_contains_expr(expr, value))
            elif op == "equals":
                conditions.append(f"LOWER(CAST({expr} AS TEXT)) = LOWER({_like_pattern(value).replace('%', '')})")
            elif op in {"gt", "lt", "gte", "lte"}:
                operator = {"gt": ">", "lt": "<", "gte": ">=", "lte": "<="}[op]
                if col is not None and col.get("dtype") in {"INTEGER", "REAL"}:
                    number = _to_float(value)
                    if number is not None:
                        conditions.append(f'{expr} {operator} {number}')
            elif op == "between":
                # Keep fallback conservative; unsupported range values are ignored.
                continue
        return " WHERE " + " AND ".join(conditions) if conditions else ""

    def _query_basic_aggregate(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        task: PlannedTask,
    ) -> str | None:
        keywords = _filter_keywords_for_question(task.text)
        search_keywords = _select_search_keywords(keywords)
        where_clause = ""
        if search_keywords:
            where_clause = " WHERE " + _search_text_conditions(search_keywords)

        if task.kind == "count":
            value_count = self._query_value_count(table, db, schema_list, task.text)
            if value_count is not None:
                return value_count
            if search_keywords and not _has_code_like_token(search_keywords):
                logger.info("excel_query_count: no categorical value resolved for table=%s", table.table_name)
                return None
            result = self._execute(
                f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}"{where_clause}',
                db,
            )
            if result and result[0] and result[0][0][0] == 0:
                return None
            return self._format_result(result) if result else None

        fn_map = {"sum": "SUM", "avg": "AVG", "max": "MAX", "min": "MIN"}
        label_map = {"sum": "Tổng", "avg": "Trung bình", "max": "Cao nhất", "min": "Thấp nhất"}
        col = _best_column(
            schema_list,
            task.text,
            {"age", "credit", "quantity", "generic_number"},
            require_numeric=True,
            min_score=70,
        )
        if col is None:
            logger.info("excel_query_%s: no metric column resolved for table=%s", task.kind, table.table_name)
            return None

        fn = fn_map[task.kind]
        label = label_map[task.kind]
        quoted_col = _sql_quote_identifier(col["name"])
        result = self._execute(
            f'SELECT {fn}({quoted_col}) AS "{col["name"]}_{label}" '
            f'FROM "{table.table_name}"{where_clause}',
            db,
        )
        if result and result[0] and all(value is None for value in result[0][0]):
            return None
        return self._format_result(result) if result else None

    def _query_value_count(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        question: str,
    ) -> str | None:
        q_norm = normalize_text(question)
        if not q_norm:
            return None

        best: tuple[float, dict, str, int] | None = None
        for col in schema_list:
            if col.get("dtype") not in {"TEXT", "BOOLEAN"}:
                continue
            col_name = col.get("name")
            if not col_name:
                continue
            quoted_col = _sql_quote_identifier(col_name)
            result = self._execute(
                f'SELECT CAST({quoted_col} AS TEXT) AS "value", COUNT(*) AS "n" '
                f'FROM "{table.table_name}" '
                f'WHERE {quoted_col} IS NOT NULL AND CAST({quoted_col} AS TEXT) != \'\' '
                f'GROUP BY CAST({quoted_col} AS TEXT) '
                f'ORDER BY "n" DESC LIMIT 200',
                db,
            )
            if not result or not result[0]:
                continue
            for value, count in result[0]:
                value_text = str(value or "").strip()
                value_norm = normalize_text(value_text)
                if not value_norm:
                    continue
                value_tokens = set(value_norm.split())
                q_tokens = set(q_norm.split())
                if value_norm in q_norm:
                    score = 1.0
                elif value_tokens and value_tokens.issubset(q_tokens):
                    score = 0.96
                elif len(value_tokens) == 1 and value_norm in q_tokens:
                    score = 0.94
                else:
                    score = _fuzzy_score(value_norm, q_norm)

                score += min(float(col.get("semantic_confidence") or 0.0), 1.0) * 0.05
                if col.get("semantic_type") in {"gender", "degree", "education_level", "department", "class_name"}:
                    score += 0.04

                if score >= 0.9 and (best is None or score > best[0]):
                    best = (score, col, value_text, int(count or 0))

        if best is None:
            return None
        _, col, value_text, _count = best
        quoted_col = _sql_quote_identifier(col["name"])
        result = self._execute(
            f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}" '
            f'WHERE LOWER(CAST({quoted_col} AS TEXT)) = LOWER({_like_pattern(value_text).replace("%", "")})',
            db,
        )
        if not result or not result[0] or result[0][0][0] == 0:
            return None
        return self._format_result(result)

    def _query_group_count(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        task: PlannedTask,
    ) -> str | None:
        group_col = self._resolve_hint_column(schema_list, task.group_by_hint, min_score=40)
        if group_col is None:
            return None
        group_expr = _sql_quote_identifier(group_col["name"])
        where_clause = self._where_clause_for_filters(schema_list, task.filters)
        sql = (
            f'SELECT {group_expr} AS "{group_col["name"]}", COUNT(*) AS "Số lượng" '
            f'FROM "{table.table_name}"{where_clause} '
            f'WHERE {group_expr} IS NOT NULL ' if not where_clause else
            f'SELECT {group_expr} AS "{group_col["name"]}", COUNT(*) AS "Số lượng" '
            f'FROM "{table.table_name}"{where_clause} AND {group_expr} IS NOT NULL '
        )
        sql += f'GROUP BY {group_expr} ORDER BY "Số lượng" DESC, {group_expr} LIMIT {SQL_MAX_ROWS}'
        result = self._execute(sql, db)
        if not result or not result[0]:
            return None
        return self._format_result(result)

    def _query_generic_aggregate(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        task: PlannedTask,
    ) -> str | None:
        if task.op == "count":
            result = self._execute(
                f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}"'
                f'{self._where_clause_for_filters(schema_list, task.filters)}',
                db,
            )
            return self._format_result(result) if result else None

        metric_col = self._resolve_hint_column(schema_list, task.metric_hint, require_numeric=True, min_score=45)
        if metric_col is None:
            return None
        fn = (task.op or "").upper()
        if fn not in {"SUM", "AVG", "MIN", "MAX"}:
            return None
        quoted_col = _sql_quote_identifier(metric_col["name"])
        where_clause = self._where_clause_for_filters(schema_list, task.filters)
        result = self._execute(
            f'SELECT {fn}({quoted_col}) AS "{metric_col["name"]}_{fn}" '
            f'FROM "{table.table_name}"{where_clause}',
            db,
        )
        if result and result[0] and all(value is None for value in result[0][0]):
            return None
        return self._format_result(result) if result else None

    def _query_generic_extreme(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
        task: PlannedTask,
    ) -> str | None:
        metric_hint = task.metric_hint or ""
        metric_norm = normalize_text(metric_hint)
        if any(token in metric_norm for token in ("tuoi", "sinh", "birth", "age")):
            if task.direction == "max":
                return self._query_oldest_person(table, db, schema_list, metric_hint + " " + " ".join(str(f.get("value", "")) for f in task.filters or []))
            return self._query_youngest_person(table, db, schema_list, metric_hint + " " + " ".join(str(f.get("value", "")) for f in task.filters or []))

        metric_col = self._resolve_hint_column(schema_list, metric_hint, require_numeric=True, min_score=45)
        if metric_col is None:
            return None
        direction = "DESC" if task.direction == "max" else "ASC"
        quoted_col = _sql_quote_identifier(metric_col["name"])
        where_clause = self._where_clause_for_filters(schema_list, task.filters)
        result = self._execute(
            f'SELECT * FROM "{table.table_name}"{where_clause} '
            f'ORDER BY {quoted_col} IS NULL ASC, {quoted_col} {direction} LIMIT 1',
            db,
        )
        if not result or not result[0]:
            return None
        return self._format_result(result)

    def _query_gender_count(
        self,
        table: ExcelTableRecord,
        db: Session,
        schema_list: list[dict],
    ) -> str | None:
        gender_col = _best_column(schema_list, "giới tính nam nữ", {"gender"}, min_score=60)
        if gender_col is None:
            return None
        col = _sql_quote_identifier(gender_col["name"])
        sql = (
            'SELECT '
            f"SUM(CASE WHEN LOWER(CAST({col} AS TEXT)) IN ('nam', 'male', 'm') THEN 1 ELSE 0 END) AS \"Nam\", "
            f"SUM(CASE WHEN CAST({col} AS TEXT) IN ('Nữ', 'nữ', 'Nu', 'nu', 'NU', 'Female', 'female', 'F', 'f') "
            f"THEN 1 ELSE 0 END) AS \"Nữ\" "
            f'FROM "{table.table_name}"'
        )
        result = self._execute(sql, db)
        if not result:
            return None
        return self._format_result(result)

    # ── RETAS queries (deterministic, no LLM) ────────────────────
    def _query_retas(
        self,
        table: ExcelTableRecord,
        db: Session,
        intent: Intent,
        keywords: list[str],
        question: str,
        schema_list: list[dict],
    ) -> str | None:
        sql: str | None = None
        if intent == Intent.LOOKUP:
            sql = self._build_lookup_sql(table, schema_list, keywords)
        elif intent == Intent.COUNT:
            sql = self._build_count_sql(table, schema_list, keywords)
        elif intent in (Intent.MAX, Intent.MIN, Intent.SUM, Intent.AVG):
            cols = _resolve_column(question, schema_list)
            if not cols:
                return None
            sql = self._build_aggr_sql(intent, cols, table, schema_list, keywords)

        if sql is None:
            return None

        result = self._execute(sql, db)
        if result is None:
            return None

        return self._format_result(result)

    def _build_lookup_sql(
        self, table: ExcelTableRecord, schema: list[dict], keywords: list[str]
    ) -> str:
        if not keywords:
            return None
        
        # Check if search_text column exists
        col_names = {c['name'] for c in schema}
        has_search_text = True
        search_keywords = _select_search_keywords(keywords)
        
        if has_search_text:
            # Normal path: use search_text
            conditions = _search_text_conditions(search_keywords)
            return (
                f'SELECT * FROM "{table.table_name}" '
                f'WHERE search_text IS NOT NULL '
                f'AND {conditions} '
                f'ORDER BY "_row_idx" LIMIT {SQL_MAX_ROWS}'
            )
        else:
            # Fallback: search across all TEXT columns (any keyword in any column)
            text_cols = [f'"{c["name"]}"' for c in schema if c['dtype'] == 'TEXT']
            if not text_cols:
                return None
            # Build: WHERE (LOWER(col1) LIKE LOWER(%kw1%) OR LOWER(col2) LIKE LOWER(%kw1%) OR ...) 
            #    AND (LOWER(col1) LIKE LOWER(%kw2%) OR LOWER(col2) LIKE LOWER(%kw2%) OR ...)
            conditions = []
            for kw in search_keywords:
                or_parts = [_contains_expr(col, kw) for col in text_cols]
                conditions.append(f'({" OR ".join(or_parts)})')
            where_clause = ' AND '.join(conditions)
            return (
                f'SELECT * FROM "{table.table_name}" '
                f'WHERE {where_clause} '
                f'ORDER BY "_row_idx" LIMIT {SQL_MAX_ROWS}'
            )

    def _build_count_sql(
        self, table: ExcelTableRecord, schema: list[dict], keywords: list[str]
    ) -> str:
        # Check if search_text column exists (added in later version)
        col_names = {c['name'] for c in schema}
        has_search_text = True
        search_keywords = _select_search_keywords(keywords)
        
        if not keywords:
            return f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}"'
        
        if not has_search_text:
            # Fallback: search across all TEXT columns (ALL keywords must match, ANY column)
            text_cols = [f'"{c["name"]}"' for c in schema if c['dtype'] == 'TEXT']
            if not text_cols:
                # No text columns → just count all
                return f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}"'
            # Build: WHERE (LOWER(col1) LIKE LOWER(%kw1%) OR LOWER(col2) LIKE LOWER(%kw1%) OR ...) 
            #    AND (LOWER(col1) LIKE LOWER(%kw2%) OR LOWER(col2) LIKE LOWER(%kw2%) OR ...)
            conditions = []
            for kw in search_keywords:
                or_parts = [_contains_expr(col, kw) for col in text_cols]
                conditions.append(f'({" OR ".join(or_parts)})')
            where_clause = ' AND '.join(conditions)
            return f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}" WHERE {where_clause}'
        
        # Normal path: search_text exists
        conditions = _search_text_conditions(search_keywords)
        return (
            f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}" '
            f'WHERE search_text IS NOT NULL '
            f'AND {conditions}'
        )

    def _build_aggr_sql(
        self,
        intent: Intent,
        cols: list[str],
        table: ExcelTableRecord,
        schema: list[dict],
        keywords: list[str],
    ) -> str:
        fn = intent.name  # MAX, MIN, SUM, AVG
        label = {"MAX": "Cao nhất", "MIN": "Thấp nhất",
                  "SUM": "Tổng", "AVG": "Trung bình"}.get(fn, fn)
        col_exprs = [f'{fn}("{c}") AS "{c}_{label}"' for c in cols]
        col_list = ', '.join(col_exprs)

        if not keywords:
            return f'SELECT {col_list} FROM "{table.table_name}"'

        # Check if search_text column exists
        col_names = {c['name'] for c in schema}
        has_search_text = True
        search_keywords = _select_search_keywords(keywords)
        
        if has_search_text:
            # Normal path: use search_text
            conditions = _search_text_conditions(search_keywords)
            return (
                f'SELECT {col_list} FROM "{table.table_name}" '
                f'WHERE search_text IS NOT NULL '
                f'AND {conditions}'
            )
        else:
            # Fallback: search across all TEXT columns (ALL keywords must match, ANY column)
            text_cols = [f'"{c["name"]}"' for c in schema if c['dtype'] == 'TEXT']
            if not text_cols:
                # No text columns → no filtering
                return f'SELECT {col_list} FROM "{table.table_name}"'
            # Build: WHERE (LOWER(col1) LIKE LOWER(%kw1%) OR LOWER(col2) LIKE LOWER(%kw1%) OR ...) 
            #    AND (LOWER(col1) LIKE LOWER(%kw2%) OR LOWER(col2) LIKE LOWER(%kw2%) OR ...)
            conditions = []
            for kw in search_keywords:
                or_parts = [_contains_expr(col, kw) for col in text_cols]
                conditions.append(f'({" OR ".join(or_parts)})')
            where_clause = ' AND '.join(conditions)
            return f'SELECT {col_list} FROM "{table.table_name}" WHERE {where_clause}'

    # ── LLM SQL generation ──────────────────────────────────────
    def _query_llm(
        self,
        table: ExcelTableRecord,
        db: Session,
        question: str,
        schema_list: list[dict],
    ) -> str | None:
        prompt = self._build_llm_prompt(table, question, schema_list)

        for attempt in range(MAX_LLM_RETRIES):
            try:
                response = self.llm.invoke(prompt)
                raw_sql = response.content.strip()

                fixer = SqlFixer(schema_list)
                sql = fixer.fix(raw_sql)

                result = self._execute(sql, db)
                if result is not None:
                    return self._format_result(result)
            except Exception as exc:
                error_msg = str(exc)[:200]
                logger.debug("llm_sql_attempt_%d_failed: %s", attempt + 1, error_msg)
                prompt += (
                    f"\n\n[Previous attempt {attempt + 1} failed: {error_msg}]\n"
                    f"Fix the SQL query and try again."
                )
                continue

        # LLM failed → RETAS LOOKUP fallback
        return None

    def _build_llm_prompt(
        self,
        table: ExcelTableRecord,
        question: str,
        schema_list: list[dict],
    ) -> str:
        sample_data_str = table.sample_data or "[]"
        try:
            samples = json.loads(sample_data_str)
        except (json.JSONDecodeError, TypeError):
            samples = []

        cols = schema_list
        col_names = [c['name'] for c in cols]

        header_line = ' | '.join(col_names)
        sep_line = ' | '.join('---' for _ in col_names)

        sample_lines: list[str] = []
        for row in samples[:3]:
            vals = [str(row.get(c, '')) for c in col_names]
            sample_lines.append(' | '.join(vals))

        if sample_lines:
            sample_block = f"| {header_line} |\n| {sep_line} |\n" + "\n".join(
                f"| {l} |" for l in sample_lines
            )
        else:
            sample_block = "(no sample data)"

        ddl_cols = '\n    '.join(
            f'"{c["name"]}" {c["dtype"]}' for c in cols
        )
        ddl = f'"{table.table_name}" (\n    "_row_idx" INTEGER NOT NULL,\n    {ddl_cols},\n    "search_text" TEXT\n)'

        examples = self._build_dynamic_examples(table.table_name, cols)

        return (
            f"You are a PostgreSQL expert. Given this table, write a SELECT query.\n\n"
            f"=== TABLE DEFINITION ===\n"
            f"CREATE TABLE {ddl};\n\n"
            f"=== SAMPLE DATA (first 3 rows) ===\n"
            f"{sample_block}\n\n"
            f"=== RULES ===\n"
            f"1. ONLY use column names from TABLE DEFINITION\n"
            f"2. Always use double quotes: \"ColumnName\"\n"
            f"3. For text search: use ILIKE, never LIKE, never =\n"
            f"4. For partial match: ILIKE '%%keyword%%' (always %% on both sides)\n"
            f"5. For multiple keywords: use AND/OR intelligently, and omit conversational words not present in the data\n"
            f"6. Use \"search_text\" for cross-column text search\n"
            f"7. ORDER BY \"_row_idx\" for detail queries\n"
            f"8. LIMIT {SQL_MAX_ROWS} for multi-row results\n"
            f"9. Use COALESCE for columns that may be NULL\n"
            f"10. For MAX/MIN/SUM/AVG: use the numeric function directly\n\n"
            f"=== EXAMPLES ===\n"
            f"{examples}\n\n"
            f"USER QUESTION: {question}\n\n"
            f"Write ONLY the SQL query, no explanation, no markdown:"
        )

    def _build_dynamic_examples(self, table_name: str, cols: list[dict]) -> str:
        text_cols = [c['name'] for c in cols if c['dtype'] == 'TEXT']
        numeric_cols = [c['name'] for c in cols if c['dtype'] in ('INTEGER', 'REAL')]
        first_text = text_cols[0] if text_cols else cols[0]['name']
        first_num = numeric_cols[0] if numeric_cols else None

        lines: list[str] = []
        lines.append(
            f"Q: cho tôi biết về int2213\n"
            f"SQL: SELECT * FROM \"{table_name}\" "
            f"WHERE \"search_text\" ILIKE ALL(ARRAY['%%int2213%%']) "
            f"ORDER BY \"_row_idx\" LIMIT {SQL_MAX_ROWS}"
        )
        lines.append(
            f"Q: có bao nhiêu môn\n"
            f"SQL: SELECT COUNT(*) AS \"Số lượng\" FROM \"{table_name}\""
        )
        if first_num:
            lines.append(
                f"Q: {first_num} cao nhất\n"
                f"SQL: SELECT MAX(\"{first_num}\") AS \"Giá trị\" FROM \"{table_name}\""
            )
            lines.append(
                f"Q: tổng {first_num} của int2213\n"
                f"SQL: SELECT SUM(\"{first_num}\") AS \"Tổng\" FROM \"{table_name}\" "
                f"WHERE \"{first_text}\" ILIKE '%%int2213%%'"
            )
        return "\n\n".join(lines)

    # ── Analysis (Python multi-query) ────────────────────────────
    def _run_analysis(
        self, tables: list[ExcelTableRecord], db: Session
    ) -> str:
        parts: list[str] = []
        for table in tables:
            schema_list = json.loads(table.column_schema)
            numeric_cols = [c['name'] for c in schema_list
                            if c['dtype'] in ('INTEGER', 'REAL')]
            text_cols = [c['name'] for c in schema_list if c['dtype'] == 'TEXT']

            part = [f"--- Sheet: {table.sheet_name} ({table.row_count} rows) ---"]

            # Row count
            result = self._execute(
                f'SELECT COUNT(*) AS "Total" FROM "{table.table_name}"', db
            )
            if result and result[0]:
                part.append(f"Tổng số dòng: {result[0][0][0]}")

            # Distinct per text column (top 10)
            for c in text_cols[:3]:
                result = self._execute(
                    f'SELECT DISTINCT "{c}" FROM "{table.table_name}" '
                    f'WHERE "{c}" IS NOT NULL AND "{c}" != \'\' '
                    f'ORDER BY "{c}" LIMIT 10', db
                )
                if result and result[0]:
                    vals = [str(r[0]) for r in result[0] if r[0] is not None]
                    part.append(f"{c} (top): {', '.join(vals)}")

            # Min/Max/Avg per numeric column
            if numeric_cols:
                aggr = ', '.join(
                    f'MIN("{c}") AS "{c}_min", '
                    f'MAX("{c}") AS "{c}_max", '
                    f'AVG("{c}") AS "{c}_avg"'
                    for c in numeric_cols[:5]
                )
                result = self._execute(
                    f'SELECT {aggr} FROM "{table.table_name}"', db
                )
                if result and result[0]:
                    r = result[0][0]
                    idx = 0
                    for c in numeric_cols[:5]:
                        vmin = r[idx] if r[idx] is not None else "?"
                        vmax = r[idx + 1] if idx + 1 < len(r) and r[idx + 1] is not None else "?"
                        vavg = f"{float(r[idx + 2]):.1f}" if idx + 2 < len(r) and r[idx + 2] is not None else "?"
                        part.append(f"{c}: Min={vmin}, Max={vmax}, TB={vavg}")
                        idx += 3

            # 5 sample rows
            result = self._execute(
                f'SELECT * FROM "{table.table_name}" '
                f'ORDER BY "_row_idx" LIMIT 5', db
            )
            if result and result[0]:
                rows, col_keys = result
                col_indices = [
                    i for i, k in enumerate(col_keys)
                    if k not in ('_row_idx', 'search_text')
                ]
                part.append("Dòng mẫu:")
                for r in rows:
                    vals = [str(r[i]) if i < len(r) and r[i] is not None else ""
                            for i in col_indices]
                    part.append(f"  | {' | '.join(vals)} |")

            parts.append("\n".join(part))

        return "\n\n".join(parts)

    # ── Execute ──────────────────────────────────────────────────
    def _execute(self, sql: str, db: Session) -> tuple[list[Any], list[str]] | None:
        try:
            result = db.execute(text(sql))
            return result.fetchall(), list(result.keys())
        except Exception as exc:
            logger.debug("sql_execute_error: %s — %s", sql[:80], exc)
            return None

    # ── Format ──────────────────────────────────────────────────
    def _format_result(self, result: tuple[list[Any], list[str]]) -> str:
        rows, col_keys = result
        if not rows:
            return "Không có kết quả phù hợp."

        col_indices = [
            i for i, k in enumerate(col_keys)
            if k not in ('_row_idx', 'search_text')
        ]
        col_names = [col_keys[i] for i in col_indices]

        lines: list[str] = []
        lines.append("| " + " | ".join(col_names) + " |")
        lines.append("| " + " | ".join(["---"] * len(col_names)) + " |")
        for row in rows:
            vals: list[str] = []
            for i in col_indices:
                v = row[i] if i < len(row) else None
                vals.append(str(v) if v is not None else "")
            lines.append("| " + " | ".join(vals) + " |")

        output = "\n".join(lines)
        if len(output) > MAX_QUERY_CHARS:
            output = output[:MAX_QUERY_CHARS] + "\n... (truncated)"
        return output


excel_query_service = ExcelQueryService()
