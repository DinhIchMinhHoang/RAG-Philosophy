from __future__ import annotations

import json
import re

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..ingest.constants import SQL_MAX_ROWS, SQL_MAX_RETRIES
from ..models import ExcelTableRecord

_SYSTEM_PROMPT = """Bạn là chuyên gia SQL. Viết câu SELECT để trả lời câu hỏi.

Quy tắc:
1. Chỉ SELECT — không DROP/DELETE/UPDATE/INSERT/ALTER
2. LIMIT {max_rows} cho kết quả nhiều
3. Dùng double quotes cho column names có khoảng trắng

Schema:
{schema}

Question:
{question}

SQL:"""

_EXAMPLES = """
Table etbl_abc_sheet: Ho_Ten TEXT, Diem REAL
Q: Ai điểm cao nhất?
SQL: SELECT "Ho_Ten", "Diem" FROM "etbl_abc_sheet" ORDER BY "Diem" DESC LIMIT 1

Q: Có bao nhiêu người?
SQL: SELECT COUNT(*) FROM "etbl_abc_sheet"
"""

_FORBIDDEN = r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE|EXEC)\b'


class ExcelQueryService:
    def __init__(self) -> None:
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            from rag_core.common.llm import build_chat_llm
            self._llm = build_chat_llm()
        return self._llm

    def get_tables(self, db: Session, user_id: str) -> list[ExcelTableRecord]:
        return db.query(ExcelTableRecord).filter(ExcelTableRecord.user_id == user_id).all()

    def _build_schema(self, tables: list[ExcelTableRecord]) -> str:
        parts = []
        for t in tables:
            cols = json.loads(t.column_schema)
            col_str = ", ".join(f"{c['name']} ({c['dtype']})" for c in cols)
            parts.append(f"Table {t.table_name} ({t.row_count} rows): {col_str}")
        return "\n".join(parts)

    def _validate_sql(self, sql: str) -> str:
        if re.search(_FORBIDDEN, sql, re.IGNORECASE):
            raise ValueError("SQL không hợp lệ")
        if not re.match(r'^\s*SELECT', sql, re.IGNORECASE):
            raise ValueError("Chỉ cho phép SELECT")
        if 'LIMIT' not in sql.upper():
            sql = sql.rstrip(';') + f" LIMIT {SQL_MAX_ROWS}"
        return sql

    def _generate_sql(self, question: str, schema: str) -> str | None:
        base_prompt = _SYSTEM_PROMPT.format(schema=schema, question=question, max_rows=SQL_MAX_ROWS)
        base_prompt += "\n" + _EXAMPLES

        error_hint = ""
        for attempt in range(SQL_MAX_RETRIES):
            try:
                prompt_with_hint = base_prompt + error_hint
                response = self.llm.invoke(prompt_with_hint)
                sql = response.content.strip()
                return self._validate_sql(sql)
            except ValueError:
                error_hint = f"\n\n[Lỗi lần {attempt + 1}: không hợp lệ] Hãy sửa lại SQL."
            except Exception:
                break
        return None

    def _execute(self, sql: str, db: Session) -> str:
        try:
            result = db.execute(text(sql))
            rows = result.fetchall()
            cols = result.keys()

            if not rows:
                return "Không có kết quả phù hợp."

            lines = []
            lines.append("| " + " | ".join(str(c) for c in cols) + " |")
            lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
            for row in rows:
                lines.append("| " + " | ".join(str(v) if v is not None else "" for v in row) + " |")
            return "\n".join(lines)
        except Exception as exc:
            return f"Lỗi SQL: {str(exc)[:200]}"

    def query(self, db: Session, user_id: str, question: str) -> str | None:
        tables = self.get_tables(db, user_id)
        if not tables:
            return None

        schema = self._build_schema(tables)
        sql = self._generate_sql(question, schema)
        if sql is None:
            return None

        return self._execute(sql, db)


excel_query_service = ExcelQueryService()