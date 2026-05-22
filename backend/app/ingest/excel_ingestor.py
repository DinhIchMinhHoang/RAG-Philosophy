from __future__ import annotations

import json
import re
import unicodedata
import uuid
from io import BytesIO

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..models import ExcelTableRecord
from .constants import (
    BATCH_SIZE,
    HEADER_CHECK_ROWS,
    HEADER_MIN_NONEMPTY_RATIO,
    MAX_FILE_SIZE_MB,
    TABLE_NAME_MAX_LEN,
    TABLE_PREFIX,
)


def _normalize_column_name(name: str) -> str:
    normalized = unicodedata.normalize('NFD', str(name))
    ascii_name = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    safe = re.sub(r'[^a-zA-Z0-9]', '_', ascii_name.strip())
    safe = re.sub(r'_+', '_', safe).strip('_')
    return safe or f"col_{uuid.uuid4().hex[:4]}"


def _find_header_row(df: pd.DataFrame) -> int:
    for i in range(min(HEADER_CHECK_ROWS, len(df))):
        row = df.iloc[i]
        non_empty = row.notna().sum() - row.astype(str).str.strip().eq('').sum()
        if non_empty >= len(df.columns) * HEADER_MIN_NONEMPTY_RATIO:
            return i
    return 0


def _infer_sql_dtype(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series):
        return "REAL"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    if pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    return "TEXT"


def _safe_table_name(document_id: str, sheet_name: str) -> str:
    safe = re.sub(r'[^a-zA-Z0-9]', '_', sheet_name.strip())[:TABLE_NAME_MAX_LEN - 12]
    safe = re.sub(r'_+', '_', safe).strip('_')
    return f"{TABLE_PREFIX}_{document_id[:8]}_{safe}"


def _create_table_ddl(table_name: str, columns: list[str], dtypes: list[str]) -> str:
    cols = ['_row_idx INTEGER']
    for col, dtype in zip(columns, dtypes):
        cols.append(f'"{col}" {dtype}')
    return f'CREATE TABLE "{table_name}" ({", ".join(cols)})'


def _ingest_dataframe(
    engine,
    df: pd.DataFrame,
    document_id: str,
    user_id: str,
    sheet_name: str,
    table_name: str,
) -> ExcelTableRecord:
    if df.empty:
        raise ValueError(f"Empty sheet: {sheet_name}")

    header_row = _find_header_row(df)
    header_df = df.iloc[header_row:]

    raw_cols = header_df.iloc[0].tolist()
    safe_cols = [_normalize_column_name(c) for c in raw_cols]

    seen: dict[str, int] = {}
    final_cols: list[str] = []
    for c in safe_cols:
        c = c or f"col_{len(final_cols)}"
        if c in seen:
            c = f"{c}_{seen[c]}"
        seen[c] = seen.get(c, 0) + 1
        final_cols.append(c)

    sample_rows = header_df.iloc[1:min(6, len(header_df))]
    dtypes = [_infer_sql_dtype(sample_rows.iloc[:, i]) for i in range(len(final_cols))]

    with engine.connect() as conn:
        # Xoá ExcelTableRecord cũ trước — tránh unique constraint violation khi re-index
        conn.execute(
            text('DELETE FROM excel_table_records WHERE document_id = :doc_id AND table_name = :tbl'),
            {"doc_id": document_id, "tbl": table_name},
        )
        conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
        conn.execute(text(_create_table_ddl(table_name, final_cols, dtypes)))
        conn.execute(text(f'CREATE INDEX IF NOT EXISTS "ix_{table_name}_row" ON "{table_name}" (_row_idx)'))
        conn.commit()

    data_df = header_df.iloc[1:].reset_index(drop=True)
    data_df.insert(0, '_row_idx', range(1, len(data_df) + 1))
    data_df.columns = ['_row_idx'] + final_cols

    data_df.to_sql(table_name, engine, if_exists='append', index=False, method='multi', chunksize=BATCH_SIZE)

    col_schema = [{"name": c, "dtype": d} for c, d in zip(final_cols, dtypes)]
    return ExcelTableRecord(
        id=str(uuid.uuid4()),
        document_id=document_id,
        user_id=user_id,
        table_name=table_name,
        sheet_name=sheet_name,
        column_schema=json.dumps(col_schema),
        row_count=len(data_df),
    )


def ingest_excel_to_sql(
    db: Session,
    file_bytes: bytes,
    file_ext: str,
    document_id: str,
    job_id: str,
    user_id: str,
) -> list[ExcelTableRecord]:
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File {size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB limit")

    engine = db.bind
    results: list[ExcelTableRecord] = []

    try:
        if file_ext == '.csv':
            df = pd.read_csv(BytesIO(file_bytes))
            table_name = _safe_table_name(document_id, "csv")
            rec = _ingest_dataframe(engine, df, document_id, user_id, "csv", table_name)
            db.add(rec)
            results.append(rec)
        else:
            xls = pd.ExcelFile(BytesIO(file_bytes))
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                table_name = _safe_table_name(document_id, sheet_name)
                rec = _ingest_dataframe(engine, df, document_id, user_id, sheet_name, table_name)
                db.add(rec)
                results.append(rec)

        db.commit()
        return results
    except Exception as exc:
        db.rollback()
        for rec in results:
            try:
                with engine.connect() as conn:
                    conn.execute(text(f'DROP TABLE IF EXISTS "{rec.table_name}"'))
                    conn.commit()
            except Exception:
                pass
        raise


def drop_excel_tables(db: Session, document_id: str) -> int:
    excel_tbls = db.query(ExcelTableRecord).filter_by(document_id=document_id).all()
    if not excel_tbls:
        return 0

    engine = db.bind
    with engine.connect() as conn:
        for tbl in excel_tbls:
            conn.execute(text(f'DROP TABLE IF EXISTS "{tbl.table_name}"'))
        conn.commit()

    count = len(excel_tbls)
    for tbl in excel_tbls:
        db.delete(tbl)
    db.commit()
    return count