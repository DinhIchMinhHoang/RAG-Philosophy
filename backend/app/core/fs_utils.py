from __future__ import annotations

from pathlib import Path
from typing import Dict


def ensure_notebook_dirs(data_root: str | Path, user_id: int, notebook_id: int) -> Dict[str, str]:
    """Create and return paths for a user's notebook structure.

    Structure created:
      [data_root]/user_{user_id}/notebook_{notebook_id}/
      [data_root]/user_{user_id}/notebook_{notebook_id}/sources/
      vector DB path: [data_root]/user_{user_id}/notebook_{notebook_id}/vector.db

    Uses pathlib.Path.mkdir(parents=True, exist_ok=True).
    Returns a dict with keys: user_root_dir, notebook_dir, sources_dir, vector_db_path
    """
    root = Path(data_root)
    user_root = root / f"user_{user_id}"
    notebook_dir = user_root / f"notebook_{notebook_id}"
    sources_dir = notebook_dir / "sources"
    vector_db = notebook_dir / "vector.db"

    user_root.mkdir(parents=True, exist_ok=True)
    notebook_dir.mkdir(parents=True, exist_ok=True)
    sources_dir.mkdir(parents=True, exist_ok=True)

    return {
        "user_root_dir": str(user_root),
        "notebook_dir": str(notebook_dir),
        "sources_dir": str(sources_dir),
        "vector_db_path": str(vector_db),
    }
