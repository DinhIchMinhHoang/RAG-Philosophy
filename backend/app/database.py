from __future__ import annotations

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .core.settings import settings


def _build_engine():
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(settings.database_url, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_runtime_schema(engine: Engine) -> None:
    """Apply small additive schema updates for local deployments without Alembic."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    required_columns = {
        "documents": {
            "owner_id": "INTEGER",
            "notebook_id": "INTEGER",
        },
        "document_chunks": {
            "owner_id": "INTEGER",
            "notebook_id": "INTEGER",
        },
        "conversations": {
            "archived_at": "TIMESTAMP",
        },
        "excel_table_records": {
            "sample_data": "TEXT",
        },
    }

    with engine.begin() as connection:
        for table_name, columns in required_columns.items():
            if table_name not in table_names:
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_type in columns.items():
                if column_name not in existing:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
