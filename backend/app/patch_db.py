"""Patch script to ALTER the users table safely.

This script will:
 - Add column user_root_dir to users if it does not exist.
 - Remove column notebook_id from users if it exists (SQLite doesn't support DROP COLUMN directly),
   so we recreate the table without notebook_id while preserving data.

Important: designed for SQLite. It will preserve existing data.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path("./rag_system.db")


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols


def add_column_if_missing(conn: sqlite3.Connection, table: str, column_def: str):
    # column_def example: 'user_root_dir TEXT'
    col_name = column_def.split()[0]
    if column_exists(conn, table, col_name):
        print(f"Column {col_name} already exists on {table}")
        return
    print(f"Adding column {col_name} to {table}")
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")


def recreate_table_without_column(conn: sqlite3.Connection, table: str, remove_cols: list[str]):
    # Get current schema
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()  # cid, name, type, notnull, dflt_value, pk
    col_names = [c[1] for c in cols if c[1] not in remove_cols]

    col_list_sql = ", ".join(col_names)
    temp_table = f"{table}__new"

    # Get create statement for original table
    cur = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
    row = cur.fetchone()
    if not row:
        raise RuntimeError(f"Table {table} does not exist")
    create_sql = row[0]

    # Build new create SQL by removing removed columns from definition
    # Simple approach: create a new table with selected columns using SELECT INTO-like pattern
    # Build columns definitions from PRAGMA
    new_cols_defs = []
    for c in cols:
        name = c[1]
        if name in remove_cols:
            continue
        typ = c[2] or "TEXT"
        notnull = "NOT NULL" if c[3] else ""
        dflt = f"DEFAULT {c[4]}" if c[4] is not None else ""
        pk = "PRIMARY KEY" if c[5] else ""
        new_cols_defs.append(f"{name} {typ} {notnull} {dflt} {pk}".strip())

    new_create_sql = f"CREATE TABLE {temp_table} ({', '.join(new_cols_defs)})"

    print("Creating temporary table:", new_create_sql)
    conn.execute(new_create_sql)

    # Copy data
    copy_sql = f"INSERT INTO {temp_table} ({col_list_sql}) SELECT {col_list_sql} FROM {table}"
    print("Copying data:", copy_sql)
    conn.execute(copy_sql)

    # Drop old table and rename new
    conn.execute(f"DROP TABLE {table}")
    conn.execute(f"ALTER TABLE {temp_table} RENAME TO {table}")
    print(f"Recreated {table} without columns: {remove_cols}")


def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Please run from project root where rag_system.db exists.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Add user_root_dir if missing
        add_column_if_missing(conn, "users", "user_root_dir TEXT")

        # If notebook_id exists, recreate table without it
        if column_exists(conn, "users", "notebook_id"):
            print("notebook_id exists — recreating users table without it")
            recreate_table_without_column(conn, "users", ["notebook_id"])
        else:
            print("notebook_id not present — no need to recreate users table")

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
