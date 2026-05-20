from __future__ import annotations

import os
from typing import List, Optional

<<<<<<< HEAD
from config import Config
=======
try:
    from ..config import Config
except ImportError:  # pragma: no cover
    from config import Config
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca


def normalize_pdf_path(path: str) -> str:
    return path.strip().strip('"').strip("'")


def collect_pdf_paths(target_pdf: Optional[str], raw_dir: Optional[str] = None) -> List[str]:
    raw_dir = raw_dir or Config.RAW_DIR

    if target_pdf:
        normalized = normalize_pdf_path(target_pdf)
        if not os.path.isfile(normalized):
            raise FileNotFoundError(f"Cannot find PDF file: {normalized}")
        return [normalized]

    pdf_files = [
        os.path.join(raw_dir, name)
        for name in os.listdir(raw_dir)
        if name.lower().endswith(".pdf")
    ]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {raw_dir}")
    return pdf_files
