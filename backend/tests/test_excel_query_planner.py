from __future__ import annotations

import json
import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import models
from backend.app.services.excel_query_service import ExcelQueryService, PlannedTask


class ExcelQueryPlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        models.Base.metadata.create_all(self.engine)
        self.db = self.SessionLocal()
        self.service = ExcelQueryService()
        self.service._plan_tasks_with_llm = lambda *_args, **_kwargs: []

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def _add_people_table(self) -> None:
        self.db.execute(text(
            'CREATE TABLE "people" ('
            '"_row_idx" INTEGER, '
            '"Ho_ten" TEXT, '
            '"Trinh_do" TEXT, '
            '"Nam_sinh" INTEGER, '
            '"TC" INTEGER, '
            'search_text TEXT)'
        ))
        rows = [
            (1, "Nguyễn Quốc Đô", "Thạc sĩ", 1988, 3),
            (2, "Trần Văn A", "Thạc sĩ", 1977, 2),
            (3, "Lê Thị B", "Đại học", 1970, 4),
            (4, "Phạm Văn C", "Thạc sĩ", 1995, 2),
        ]
        for row in rows:
            search_text = " ".join(str(v) for v in row[1:])
            self.db.execute(
                text(
                    'INSERT INTO "people" ("_row_idx", "Ho_ten", "Trinh_do", "Nam_sinh", "TC", search_text) '
                    'VALUES (:idx, :name, :degree, :year, :tc, :search_text)'
                ),
                {
                    "idx": row[0],
                    "name": row[1],
                    "degree": row[2],
                    "year": row[3],
                    "tc": row[4],
                    "search_text": search_text,
                },
            )
        schema = [
            {
                "name": "Ho_ten",
                "original_name": "Họ tên",
                "dtype": "TEXT",
                "semantic_type": "person_name",
                "semantic_confidence": 0.9,
                "aliases": ["họ tên", "tên người"],
            },
            {
                "name": "Trinh_do",
                "original_name": "Trình độ",
                "dtype": "TEXT",
                "semantic_type": "degree",
                "semantic_confidence": 0.9,
                "aliases": ["trình độ", "học vị"],
            },
            {
                "name": "Nam_sinh",
                "original_name": "Năm sinh",
                "dtype": "INTEGER",
                "semantic_type": "birth_year",
                "semantic_confidence": 0.95,
                "aliases": ["năm sinh", "tuổi"],
            },
            {
                "name": "TC",
                "original_name": "TC",
                "dtype": "INTEGER",
                "semantic_type": "credit",
                "semantic_confidence": 0.9,
                "aliases": ["tín chỉ"],
            },
        ]
        self.db.add(
            models.ExcelTableRecord(
                id="tbl-1",
                document_id="doc-1",
                user_id="user-1",
                table_name="people",
                sheet_name="Sheet1",
                column_schema=json.dumps(schema, ensure_ascii=False),
                sample_data="[]",
                row_count=4,
            )
        )
        self.db.commit()

    def test_compound_lookup_and_oldest_person_uses_birth_year_not_credit(self) -> None:
        self._add_people_table()

        result = self.service.query(
            self.db,
            "user-1",
            "hãy cho tôi thông tin về Nguyễn Quốc Đô và ai là người lớn tuổi nhất trong danh sách học thạc sĩ",
        )

        self.assertIsNotNone(result)
        self.assertIn("Nguyễn Quốc Đô", result)
        self.assertIn("Trần Văn A", result)
        self.assertNotIn("TC_Cao nhất", result)

    def test_compound_lookup_and_youngest_person_uses_birth_year_desc(self) -> None:
        self._add_people_table()

        result = self.service.query(
            self.db,
            "user-1",
            "hãy cho tôi thông tin về Nguyễn Quốc Đô và ai là người nhỏ tuổi nhất trong danh sách học thạc sĩ",
        )

        self.assertIsNotNone(result)
        self.assertIn("Thông tin về Nguyễn Quốc Đô", result)
        self.assertIn("Người nhỏ tuổi nhất", result)
        self.assertIn("Nguyễn Quốc Đô", result)
        self.assertIn("Phạm Văn C", result)
        self.assertNotIn("TC_Thấp nhất", result)

    def test_youngest_person_handles_timestamp_birth_date_column(self) -> None:
        self.db.execute(text(
            'CREATE TABLE "degrees" ('
            '"_row_idx" INTEGER, '
            '"Ten_VBCC" TEXT, '
            '"Ho_va_ten" TEXT, '
            '"Ngay_thang_nam_sinh" TEXT, '
            'search_text TEXT)'
        ))
        rows = [
            (1, "Thạc Sĩ", "Nguyễn Quốc Đô", "1991-03-16 00:00:00"),
            (2, "Thạc Sĩ", "Trần Văn A", "1997-01-20 00:00:00"),
            (3, "Đại học", "Lê Thị B", "2000-05-10 00:00:00"),
        ]
        for row in rows:
            self.db.execute(
                text(
                    'INSERT INTO "degrees" ("_row_idx", "Ten_VBCC", "Ho_va_ten", "Ngay_thang_nam_sinh", search_text) '
                    'VALUES (:idx, :degree, :name, :dob, :search_text)'
                ),
                {
                    "idx": row[0],
                    "degree": row[1],
                    "name": row[2],
                    "dob": row[3],
                    "search_text": " ".join(str(v) for v in row[1:]),
                },
            )
        schema = [
            {
                "name": "Ten_VBCC",
                "original_name": "Ten_VBCC",
                "dtype": "TEXT",
                "semantic_type": "generic_text",
            },
            {
                "name": "Ho_va_ten",
                "original_name": "Họ và tên",
                "dtype": "TEXT",
                "semantic_type": "person_name",
                "semantic_confidence": 0.9,
            },
            {
                "name": "Ngay_thang_nam_sinh",
                "original_name": "Ngày tháng năm sinh",
                "dtype": "TIMESTAMP",
                "semantic_type": "birth_year",
                "semantic_confidence": 0.95,
            },
        ]
        self.db.add(
            models.ExcelTableRecord(
                id="tbl-3",
                document_id="doc-3",
                user_id="user-1",
                table_name="degrees",
                sheet_name="Sheet1",
                column_schema=json.dumps(schema, ensure_ascii=False),
                sample_data="[]",
                row_count=3,
            )
        )
        self.db.commit()

        result = self.service.query(
            self.db,
            "user-1",
            "Hãy cho tôi thông tin về Nguyễn Quốc Đô và ai là người NHỎ tuổi\n     nhất trong danh sách học thạc sĩ?",
        )

        self.assertIsNotNone(result)
        self.assertIn("Thông tin về Nguyễn Quốc Đô", result)
        self.assertIn("Người nhỏ tuổi nhất", result)
        self.assertIn("Nguyễn Quốc Đô", result)
        self.assertIn("Trần Văn A", result)

    def test_lookup_typo_and_gender_count_are_both_answered(self) -> None:
        self.db.execute(text(
            'CREATE TABLE "degree_people" ('
            '"_row_idx" INTEGER, '
            '"Ho_va_ten" TEXT, '
            '"Gioi_tinh" TEXT, '
            '"Ten_VBCC" TEXT, '
            'search_text TEXT)'
        ))
        rows = [
            (1, "Trần Quốc Trình", "Nam", "Thạc Sĩ"),
            (2, "Nguyễn Quốc Đô", "Nam", "Thạc Sĩ"),
            (3, "Lê Thị B", "Nữ", "Thạc Sĩ"),
            (4, "Phạm Thị C", "Nữ", "Đại học"),
        ]
        for row in rows:
            self.db.execute(
                text(
                    'INSERT INTO "degree_people" ("_row_idx", "Ho_va_ten", "Gioi_tinh", "Ten_VBCC", search_text) '
                    'VALUES (:idx, :name, :gender, :degree, :search_text)'
                ),
                {
                    "idx": row[0],
                    "name": row[1],
                    "gender": row[2],
                    "degree": row[3],
                    "search_text": " ".join(str(v) for v in row[1:]),
                },
            )
        schema = [
            {
                "name": "Ho_va_ten",
                "original_name": "Họ và tên",
                "dtype": "TEXT",
                "semantic_type": "person_name",
                "semantic_confidence": 0.9,
            },
            {
                "name": "Gioi_tinh",
                "original_name": "Giới tính",
                "dtype": "TEXT",
                "semantic_type": "generic_text",
            },
            {
                "name": "Ten_VBCC",
                "original_name": "Tên VBCC",
                "dtype": "TEXT",
                "semantic_type": "generic_text",
            },
        ]
        self.db.add(
            models.ExcelTableRecord(
                id="tbl-4",
                document_id="doc-4",
                user_id="user-1",
                table_name="degree_people",
                sheet_name="Sheet1",
                column_schema=json.dumps(schema, ensure_ascii=False),
                sample_data="[]",
                row_count=4,
            )
        )
        self.db.commit()

        result = self.service.query(
            self.db,
            "user-1",
            "hãy cho tôi biết về trần quốc trìnhj và cho tôi biết danh sách trên có bao nhiêu năm và bao nhiêu nữ",
        )

        self.assertIsNotNone(result)
        self.assertIn("Thông tin về trần quốc trìnhj", result)
        self.assertIn("Trần Quốc Trình", result)
        self.assertIn("Thống kê giới tính", result)
        self.assertIn("| Nam | Nữ |", result)
        self.assertIn("| 2 | 2 |", result)
        self.assertNotIn("Kết quả đếm", result)

    def test_llm_plan_group_count_handles_natural_gender_words(self) -> None:
        self.db.execute(text(
            'CREATE TABLE "degree_people_llm" ('
            '"_row_idx" INTEGER, '
            '"Ho_va_ten" TEXT, '
            '"Gioi_tinh" TEXT, '
            'search_text TEXT)'
        ))
        rows = [
            (1, "Trần Quốc Trình", "Nam"),
            (2, "Nguyễn Quốc Đô", "Nam"),
            (3, "Lê Thị B", "Nữ"),
        ]
        for row in rows:
            self.db.execute(
                text(
                    'INSERT INTO "degree_people_llm" ("_row_idx", "Ho_va_ten", "Gioi_tinh", search_text) '
                    'VALUES (:idx, :name, :gender, :search_text)'
                ),
                {
                    "idx": row[0],
                    "name": row[1],
                    "gender": row[2],
                    "search_text": " ".join(str(v) for v in row[1:]),
                },
            )
        schema = [
            {
                "name": "Ho_va_ten",
                "original_name": "Họ và tên",
                "dtype": "TEXT",
                "semantic_type": "person_name",
                "semantic_confidence": 0.9,
            },
            {
                "name": "Gioi_tinh",
                "original_name": "Giới tính",
                "dtype": "TEXT",
                "semantic_type": "generic_text",
            },
        ]
        self.db.add(
            models.ExcelTableRecord(
                id="tbl-5",
                document_id="doc-5",
                user_id="user-1",
                table_name="degree_people_llm",
                sheet_name="Sheet1",
                column_schema=json.dumps(schema, ensure_ascii=False),
                sample_data="[]",
                row_count=3,
            )
        )
        self.db.commit()

        self.service._plan_tasks_with_llm = lambda *_args, **_kwargs: [
            PlannedTask("group_count", "q", group_by_hint="giới tính", value_hints=["con trai", "con gái"])
        ]

        result = self.service.query(
            self.db,
            "user-1",
            "danh sách này có bao nhiêu con trai và bao nhiêu con gái",
        )

        self.assertIsNotNone(result)
        self.assertIn("Thống kê theo giới tính", result)
        self.assertIn("| Gioi_tinh | Số lượng |", result)
        self.assertIn("| Nam | 2 |", result)
        self.assertIn("| Nữ | 1 |", result)

    def test_single_gender_count_uses_gender_value_not_search_text(self) -> None:
        self.db.execute(text(
            'CREATE TABLE "nationality_only" ('
            '"_row_idx" INTEGER, '
            '"Ho_va_ten" TEXT, '
            '"Quoc_tich" TEXT, '
            'search_text TEXT)'
        ))
        for idx in range(1, 41):
            self.db.execute(
                text(
                    'INSERT INTO "nationality_only" ("_row_idx", "Ho_va_ten", "Quoc_tich", search_text) '
                    'VALUES (:idx, :name, :nationality, :search_text)'
                ),
                {
                    "idx": idx,
                    "name": f"Người {idx}",
                    "nationality": "Việt Nam",
                    "search_text": f"Người {idx} Việt Nam",
                },
            )
        self.db.add(
            models.ExcelTableRecord(
                id="tbl-nationality",
                document_id="doc-nationality",
                user_id="user-1",
                table_name="nationality_only",
                sheet_name="Nationality",
                column_schema=json.dumps([
                    {"name": "Ho_va_ten", "original_name": "Họ và tên", "dtype": "TEXT"},
                    {"name": "Quoc_tich", "original_name": "Quốc tịch", "dtype": "TEXT"},
                ], ensure_ascii=False),
                sample_data="[]",
                row_count=40,
            )
        )

        self.db.execute(text(
            'CREATE TABLE "gender_people" ('
            '"_row_idx" INTEGER, '
            '"Ho_va_ten" TEXT, '
            '"Gioi_tinh" TEXT, '
            'search_text TEXT)'
        ))
        for idx in range(1, 51):
            gender = "Nam" if idx <= 45 else "Nữ"
            self.db.execute(
                text(
                    'INSERT INTO "gender_people" ("_row_idx", "Ho_va_ten", "Gioi_tinh", search_text) '
                    'VALUES (:idx, :name, :gender, :search_text)'
                ),
                {
                    "idx": idx,
                    "name": f"Học viên {idx}",
                    "gender": gender,
                    "search_text": f"Học viên {idx} {gender}",
                },
            )
        self.db.add(
            models.ExcelTableRecord(
                id="tbl-gender",
                document_id="doc-gender",
                user_id="user-1",
                table_name="gender_people",
                sheet_name="Gender",
                column_schema=json.dumps([
                    {"name": "Ho_va_ten", "original_name": "Họ và tên", "dtype": "TEXT", "semantic_type": "person_name"},
                    {"name": "Gioi_tinh", "original_name": "Giới tính", "dtype": "TEXT", "semantic_type": "gender"},
                ], ensure_ascii=False),
                sample_data="[]",
                row_count=50,
            )
        )
        self.db.commit()

        result = self.service.query(self.db, "user-1", "có bao nhiêu nam trong danh sách")

        self.assertIsNotNone(result)
        self.assertIn("| Số lượng |", result)
        self.assertIn("| 45 |", result)
        self.assertNotIn("| 40 |", result)

    def test_oldest_person_returns_none_when_no_age_or_birth_column(self) -> None:
        self.db.execute(text(
            'CREATE TABLE "classes" ('
            '"_row_idx" INTEGER, '
            '"Ten" TEXT, '
            '"TC" INTEGER, '
            'search_text TEXT)'
        ))
        self.db.execute(text(
            'INSERT INTO "classes" ("_row_idx", "Ten", "TC", search_text) '
            "VALUES (1, 'Nguyễn Quốc Đô', 3, 'Nguyễn Quốc Đô 3')"
        ))
        schema = [
            {"name": "Ten", "original_name": "Tên", "dtype": "TEXT"},
            {"name": "TC", "original_name": "TC", "dtype": "INTEGER"},
        ]
        self.db.add(
            models.ExcelTableRecord(
                id="tbl-2",
                document_id="doc-2",
                user_id="user-1",
                table_name="classes",
                sheet_name="Sheet1",
                column_schema=json.dumps(schema, ensure_ascii=False),
                sample_data="[]",
                row_count=1,
            )
        )
        self.db.commit()

        result = self.service.query(
            self.db,
            "user-1",
            "ai là người lớn tuổi nhất trong danh sách",
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
