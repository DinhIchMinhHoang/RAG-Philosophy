from __future__ import annotations

import json
import re
import logging
from enum import Enum
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..ingest.constants import SQL_MAX_ROWS, MAX_LLM_RETRIES
from ..models import ExcelTableRecord

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


def _extract_keywords(question: str) -> list[str]:
    tokens = re.findall(r'[A-Za-z0-9\u00C0-\u1EF9]+', question.lower())
    keywords = []
    for t in tokens:
        if t in _STOPWORDS:
            continue
        keywords.append(t)
    return keywords


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

    return matched[:3] if matched else numeric[:3]


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
        schema_list = json.loads(table.column_schema)

        try:
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
        has_search_text = 'search_text' in col_names
        
        if has_search_text:
            # Normal path: use search_text
            conditions = ' AND '.join(f"search_text LIKE '%{kw}%'" for kw in keywords)
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
            # Build: WHERE (col1 LIKE %kw1% OR col2 LIKE %kw1% OR ...) 
            #    AND (col1 LIKE %kw2% OR col2 LIKE %kw2% OR ...)
            conditions = []
            for kw in keywords:
                or_parts = [f'{col} LIKE \'%{kw}%\'' for col in text_cols]
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
        has_search_text = 'search_text' in col_names
        
        if not keywords:
            return f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}"'
        
        if not has_search_text:
            # Fallback: search across all TEXT columns (ALL keywords must match, ANY column)
            text_cols = [f'"{c["name"]}"' for c in schema if c['dtype'] == 'TEXT']
            if not text_cols:
                # No text columns → just count all
                return f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}"'
            # Build: WHERE (col1 LIKE %kw1% OR col2 LIKE %kw1% OR ...) 
            #    AND (col1 LIKE %kw2% OR col2 LIKE %kw2% OR ...)
            conditions = []
            for kw in keywords:
                or_parts = [f'{col} LIKE \'%{kw}%\'' for col in text_cols]
                conditions.append(f'({" OR ".join(or_parts)})')
            where_clause = ' AND '.join(conditions)
            return f'SELECT COUNT(*) AS "Số lượng" FROM "{table.table_name}" WHERE {where_clause}'
        
        # Normal path: search_text exists
        conditions = ' AND '.join(f"search_text LIKE '%{kw}%'" for kw in keywords)
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
        has_search_text = 'search_text' in col_names
        
        if has_search_text:
            # Normal path: use search_text
            conditions = ' AND '.join(f"search_text LIKE '%{kw}%'" for kw in keywords)
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
            # Build: WHERE (col1 LIKE %kw1% OR col2 LIKE %kw1% OR ...) 
            #    AND (col1 LIKE %kw2% OR col2 LIKE %kw2% OR ...)
            conditions = []
            for kw in keywords:
                or_parts = [f'{col} LIKE \'%{kw}%\'' for col in text_cols]
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
