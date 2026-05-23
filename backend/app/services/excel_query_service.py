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
4. Dùng UPPER() + LIKE để match không phân biệt hoa/thường, vì user có thể nhập sai
5. Nếu câu hỏi có thêm từ thừa (VD "int2213 1"), hãy dùng LIKE '%int2213%' để match
6. ORDER BY _row_idx để kết quả có thứ tự

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

Q: cho tôi biết về INT2213 1
SQL: SELECT * FROM "etbl_abc_sheet" WHERE UPPER("Mã HP") LIKE UPPER('%INT2213%') ORDER BY _row_idx LIMIT 20
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
        records = db.query(ExcelTableRecord).filter(ExcelTableRecord.user_id == user_id).all()
        if records:
            return records
        # Fallback: nếu username đã đổi, tìm theo DocumentRecord.owner_id (int)
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
        except Exception:
            pass
        return records

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

    MAX_QUERY_CHARS: int = 5000

    def _execute(self, sql: str, db: Session) -> str:
        try:
            result = db.execute(text(sql))
            rows = result.fetchall()
            cols = result.keys()

            if not rows:
                return "Không có kết quả phù hợp."

            # Loại _row_idx column (internal counter, không hiển thị cho user)
            display_cols = [c for c in cols if c != '_row_idx']
            col_indices = [i for i, c in enumerate(cols) if c != '_row_idx']

            lines = []
            lines.append("| " + " | ".join(str(c) for c in display_cols) + " |")
            lines.append("| " + " | ".join(["---"] * len(display_cols)) + " |")
            for row in rows:
                vals = [str(row[i]) if row[i] is not None else "" for i in col_indices]
                lines.append("| " + " | ".join(vals) + " |")

            output = "\n".join(lines)
            if len(output) > self.MAX_QUERY_CHARS:
                output = output[:self.MAX_QUERY_CHARS] + "\n... (truncated)"
            return output
        except Exception as exc:
            return f"Lỗi SQL: {str(exc)[:200]}"

    def _get_search_cols(self, table: ExcelTableRecord) -> list[str]:
        try:
            cols = json.loads(table.column_schema)
        except Exception:
            cols = []
        preferred = [c['name'] for c in cols if c['name'] in ('Ma_HP', 'Mon', 'Lop', 'Ten', 'Name', 'Ho_Ten')]
        if preferred:
            return preferred
        return [cols[0]['name']] if cols else []

    def _fallback_sql(self, question: str, tables: list[ExcelTableRecord]) -> str | None:
        """Fallback: extract first meaningful keyword and build simple LIKE query.
        Used when LLM-based SQL generation fails (e.g., rate limited).
        Searches ALL tables via UNION.
        """
        _STOPWORDS = frozenset({
            'cho', 'tôi', 'biết', 'về', 'của', 'và', 'các', 'có', 'là',
            'không', 'gì', 'nào', 'thế', 'này', 'một', 'những', 'được',
            'với', 'hoặc', 'hay', 'ra', 'lên', 'xuống', 'qua', 'lại',
            'khi', 'đã', 'đang', 'sẽ', 'số', 'mấy', 'nhiêu', 'bao',
            'bạn', 'em', 'anh', 'chị', 'thầy', 'cô',
        })
        all_tokens = re.findall(r'[A-Za-z0-9\u00C0-\u1EF9]+', question)
        tokens = [t for t in all_tokens if t.lower() not in _STOPWORDS and len(t) >= 3 and len(t) <= 30]
        if not tokens or not tables:
            return None
        kw = tokens[0][:50]

        selects = []
        for table in tables:
            search_cols = self._get_search_cols(table)
            if not search_cols:
                continue
            conditions = ' OR '.join(f'UPPER("{c}") LIKE UPPER(\'%{kw}%\')' for c in search_cols)
            selects.append(
                f'SELECT \'{table.sheet_name}\' AS "Sheet", * FROM "{table.table_name}" WHERE {conditions}'
            )

        if not selects:
            return None
        sql = ' UNION '.join(selects) + f' ORDER BY _row_idx LIMIT {SQL_MAX_ROWS}'
        try:
            return self._validate_sql(sql)
        except ValueError:
            return None

    def query(self, db: Session, user_id: str, question: str) -> str | None:
        tables = self.get_tables(db, user_id)
        if not tables:
            return None

        schema = self._build_schema(tables)
        sql = self._generate_sql(question, schema)
        if sql is None:
            sql = self._fallback_sql(question, tables)
        if sql is None:
            return None

        return self._execute(sql, db)


excel_query_service = ExcelQueryService()