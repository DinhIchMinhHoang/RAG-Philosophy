from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", str(value or ""))
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def normalize_text(value: Any) -> str:
    text = strip_accents(str(value or "")).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def compact_text(value: Any) -> str:
    return normalize_text(value).replace(" ", "")


def sample_values(values: list[Any], limit: int = 12) -> list[str]:
    samples: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text or text.lower() == "nan":
            continue
        key = normalize_text(text)
        if key in seen:
            continue
        seen.add(key)
        samples.append(text[:120])
        if len(samples) >= limit:
            break
    return samples


_DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b")
_YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")
_COURSE_CODE_RE = re.compile(r"^[a-z]{2,}\d{3,}[a-z0-9-]*$", re.I)


def _ratio(values: list[str], predicate) -> float:
    if not values:
        return 0.0
    return sum(1 for value in values if predicate(value)) / len(values)


def _looks_like_person(value: str) -> bool:
    norm = normalize_text(value)
    parts = norm.split()
    if not 2 <= len(parts) <= 6:
        return False
    if any(part.isdigit() for part in parts):
        return False
    return all(len(part) >= 2 for part in parts)


def _looks_like_date(value: str) -> bool:
    if isinstance(value, (date, datetime)):
        return True
    return bool(_DATE_RE.search(str(value)))


def _looks_like_year(value: str) -> bool:
    text = str(value).strip()
    return bool(_YEAR_RE.match(text))


def _looks_like_age(value: str) -> bool:
    try:
        age = float(str(value).strip())
    except ValueError:
        return False
    return 10 <= age <= 100


def _looks_like_course_code(value: str) -> bool:
    return bool(_COURSE_CODE_RE.match(str(value).strip()))


def _looks_like_gender(value: str) -> bool:
    norm = normalize_text(value)
    return norm in {"nam", "nu", "male", "female", "m", "f"}


_ALIASES: dict[str, list[str]] = {
    "person_name": ["ho ten", "ten nguoi", "can bo", "giang vien", "hoc vien", "sinh vien", "nhan su"],
    "date_of_birth": ["ngay sinh", "sinh ngay", "dob", "birthday", "tuoi", "lon tuoi", "cao tuoi"],
    "birth_year": ["nam sinh", "birth year", "tuoi", "lon tuoi", "cao tuoi"],
    "age": ["tuoi", "age", "lon tuoi", "cao tuoi"],
    "degree": ["hoc vi", "trinh do", "bang cap", "thac si", "tien si", "dai hoc", "degree"],
    "education_level": ["trinh do", "dao tao", "he dao tao", "chuong trinh", "hoc", "thac si"],
    "course_code": ["ma hoc phan", "ma hp", "ma mon", "course code"],
    "course_name": ["hoc phan", "ten mon", "mon hoc", "course name"],
    "class_name": ["lop", "lop hoc", "nhom lop", "class"],
    "credit": ["tin chi", "tc", "so tin chi", "credit"],
    "quantity": ["so luong", "si so", "ss", "quantity", "count"],
    "teacher": ["giang vien", "giao vien", "can bo giang day", "pcgd", "teacher"],
    "department": ["khoa", "bo mon", "don vi", "phong ban", "department"],
    "gender": ["gioi tinh", "nam", "nu", "male", "female", "sex"],
    "generic_text": [],
    "generic_number": [],
}


def aliases_for(semantic_type: str) -> list[str]:
    return _ALIASES.get(semantic_type, [])


def build_column_profile(
    *,
    original_name: Any,
    safe_name: str,
    dtype: str,
    values: list[Any],
) -> dict[str, Any]:
    samples = sample_values(values)
    name_norm = normalize_text(f"{original_name} {safe_name}")
    name_compact = compact_text(f"{original_name} {safe_name}")
    non_empty = [str(v).strip() for v in values if v is not None and str(v).strip() and str(v).strip().lower() != "nan"]
    non_empty_ratio = len(non_empty) / len(values) if values else 0.0
    unique_ratio = len({normalize_text(v) for v in non_empty}) / len(non_empty) if non_empty else 0.0

    semantic_type = "generic_number" if dtype in {"INTEGER", "REAL"} else "generic_text"
    confidence = 0.35

    if (
        any(token in name_compact for token in ("ngaysinh", "ngaythangnamsinh", "sinhngay", "dob", "birthday"))
        or ("ngay" in name_compact and "sinh" in name_compact)
    ):
        semantic_type, confidence = "date_of_birth", 0.95
    elif any(token in name_compact for token in ("namsinh", "birthyear")):
        semantic_type, confidence = "birth_year", 0.95
    elif "tuoi" in name_compact or name_compact == "age":
        semantic_type, confidence = "age", 0.95
    elif any(token in name_compact for token in ("hoten", "hovaten", "tennguoi", "hocvien", "sinhvien", "canbo")):
        semantic_type, confidence = "person_name", 0.9
    elif any(token in name_compact for token in ("hocvi", "trinhdo", "bangcap", "hedaotao", "chuongtrinh")):
        semantic_type, confidence = "degree", 0.9
    elif any(token in name_compact for token in ("mahp", "mahocphan", "mamon", "coursecode")):
        semantic_type, confidence = "course_code", 0.9
    elif any(token in name_compact for token in ("tenmon", "monhoc", "hocphan", "coursename")):
        semantic_type, confidence = "course_name", 0.85
    elif "lop" in name_compact or name_compact == "class":
        semantic_type, confidence = "class_name", 0.8
    elif any(token in name_compact for token in ("tinchi", "sotinchi", "credit")) or name_norm == "tc":
        semantic_type, confidence = "credit", 0.9
    elif any(token in name_compact for token in ("soluong", "siso", "quantity")) or name_norm == "ss":
        semantic_type, confidence = "quantity", 0.85
    elif any(token in name_compact for token in ("giangvien", "giaovien", "pcgd", "teacher")):
        semantic_type, confidence = "teacher", 0.85
    elif any(token in name_compact for token in ("khoa", "bomon", "donvi", "phongban", "department")):
        semantic_type, confidence = "department", 0.8
    elif any(token in name_compact for token in ("gioitinh", "gender", "sex")):
        semantic_type, confidence = "gender", 0.95
    elif samples:
        if _ratio(samples, _looks_like_date) >= 0.6:
            semantic_type, confidence = "date_of_birth", 0.75
        elif _ratio(samples, _looks_like_year) >= 0.8:
            semantic_type, confidence = "birth_year", 0.7
        elif dtype in {"INTEGER", "REAL"} and _ratio(samples, _looks_like_age) >= 0.8:
            semantic_type, confidence = "age", 0.65
        elif _ratio(samples, _looks_like_course_code) >= 0.5:
            semantic_type, confidence = "course_code", 0.7
        elif _ratio(samples, _looks_like_gender) >= 0.7:
            semantic_type, confidence = "gender", 0.75
        elif unique_ratio > 0.7 and _ratio(samples, _looks_like_person) >= 0.6:
            semantic_type, confidence = "person_name", 0.65

    return {
        "name": safe_name,
        "original_name": str(original_name),
        "dtype": dtype,
        "semantic_type": semantic_type,
        "semantic_confidence": confidence,
        "aliases": aliases_for(semantic_type),
        "sample_values": samples,
        "non_empty_ratio": round(non_empty_ratio, 3),
        "unique_ratio": round(unique_ratio, 3),
    }
