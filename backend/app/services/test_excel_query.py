"""Unit tests for the Hybrid RETAS + LLM-SQL excel query service."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_project_root = Path(__file__).resolve().parent.parent.parent.parent
_backend = _project_root / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from sqlalchemy import text

from app.services.excel_query_service import (
    _extract_keywords,
    _classify_intent,
    _resolve_column,
    SqlFixer,
    Intent,
    ExcelQueryService,
)


class TestExtractKeywords(unittest.TestCase):
    """Test keyword extraction from user questions."""

    def test_basic_lookup(self):
        """cho tôi biết về int2213 → ['int2213']"""
        self.assertEqual(_extract_keywords("cho tôi biết về int2213"), ["int2213"])

    def test_single_digit_filtered(self):
        """'1' alone → []"""
        self.assertEqual(_extract_keywords("1"), [])

    def test_single_digit_with_text(self):
        """'int2213 1' → '1' filtered, only 'int2213' kept"""
        result = _extract_keywords("cho tôi biết về int2213 1")
        self.assertEqual(result, ["int2213"])

    def test_b2_kept(self):
        """'b2' is alphanumeric, not pure digit → kept; 'anh' is a stopword → filtered"""
        result = _extract_keywords("tiếng anh b2")
        self.assertIn("b2", result)
        self.assertIn("tiếng", result)
        # 'anh' is a Vietnamese stopword, so it's filtered out

    def test_vietnamese_stopwords_removed(self):
        """Vietnamese stopwords should be removed"""
        result = _extract_keywords("có bao nhiêu môn")
        self.assertNotIn("có", result)
        self.assertNotIn("bao", result)
        self.assertNotIn("nhiêu", result)
        self.assertIn("môn", result)

    def test_count_keywords(self):
        """'bao nhiêu lớp' → ['lớp'] after stopword removal"""
        result = _extract_keywords("bao nhiêu lớp")
        self.assertEqual(result, ["lớp"])

    def test_empty_question(self):
        """Empty string → []"""
        self.assertEqual(_extract_keywords(""), [])

    def test_all_stopwords(self):
        """Only stopwords → []"""
        self.assertEqual(_extract_keywords("cho tôi và các bạn"), [])


class TestClassifyIntent(unittest.TestCase):
    """Test intent classification."""

    def test_count_bao_nhieu(self):
        """'bao nhiêu' → COUNT"""
        self.assertEqual(_classify_intent("có bao nhiêu môn", ["môn"]), Intent.COUNT)

    def test_count_may(self):
        """'mấy' → COUNT"""
        self.assertEqual(_classify_intent("có mấy môn", ["môn"]), Intent.COUNT)

    def test_count_so_luong(self):
        """'số lượng' → COUNT"""
        self.assertEqual(_classify_intent("số lượng sinh viên", ["sinh", "viên"]), Intent.COUNT)

    def test_max_cao_nhat(self):
        """'cao nhất' → MAX"""
        self.assertEqual(_classify_intent("ai điểm cao nhất", ["điểm"]), Intent.MAX)

    def test_max_nhieu_nhat(self):
        """'nhiều nhất' → MAX"""
        self.assertEqual(_classify_intent("môn nhiều tín nhất", ["tín"]), Intent.MAX)

    def test_min_thap_nhat(self):
        """'thấp nhất' → MIN"""
        self.assertEqual(_classify_intent("điểm thấp nhất", ["điểm"]), Intent.MIN)

    def test_min_it_nhat(self):
        """'ít nhất' → MIN"""
        self.assertEqual(_classify_intent("môn ít tín nhất", ["tín"]), Intent.MIN)

    def test_sum(self):
        """'tổng' → SUM"""
        kw = _extract_keywords("tổng số tín")
        self.assertEqual(_classify_intent("tổng số tín", kw), Intent.SUM)

    def test_avg(self):
        """'trung bình' → AVG"""
        self.assertEqual(_classify_intent("điểm trung bình", ["điểm"]), Intent.AVG)

    def test_lookup_default(self):
        """No pattern match + keywords → LOOKUP"""
        self.assertEqual(_classify_intent("cho tôi biết về int2213", ["int2213"]), Intent.LOOKUP)

    def test_lookup_no_keywords(self):
        """No pattern + no keywords → NONE"""
        self.assertEqual(_classify_intent("1", []), Intent.NONE)

    def test_llm_compound(self):
        """'vừa...vừa' → LLM_COMPOUND"""
        self.assertEqual(
            _classify_intent("môn nào vừa điểm cao vừa ít tín", ["điểm", "tín"]),
            Intent.LLM_COMPOUND,
        )

    def test_llm_compare(self):
        """'so sánh' → LLM_COMPARE"""
        self.assertEqual(
            _classify_intent("so sánh INT2213 và INT2201", ["int2213", "int2201"]),
            Intent.LLM_COMPARE,
        )

    def test_llm_analysis(self):
        """'phân tích' → LLM_ANALYSIS"""
        self.assertEqual(
            _classify_intent("phân tích dữ liệu", ["dữ", "liệu"]),
            Intent.LLM_ANALYSIS,
        )

    def test_llm_analysis_plan(self):
        """'tạo plan' → LLM_ANALYSIS"""
        self.assertEqual(
            _classify_intent("tạo plan học tập cho tôi", ["học", "tập"]),
            Intent.LLM_ANALYSIS,
        )

    def test_llm_filter(self):
        """'trong đó' → LLM_FILTER"""
        self.assertEqual(
            _classify_intent("môn có điểm > 8 trong đó", ["điểm"]),
            Intent.LLM_FILTER,
        )


class TestColumnResolver(unittest.TestCase):
    """Test column resolver — must work for any domain, no hardcode."""

    def setUp(self):
        self.edu_schema = [
            {"name": "Ma_HP", "dtype": "TEXT"},
            {"name": "Mon", "dtype": "TEXT"},
            {"name": "TC", "dtype": "INTEGER"},
            {"name": "LT", "dtype": "INTEGER"},
            {"name": "TH", "dtype": "INTEGER"},
        ]
        self.inv_schema = [
            {"name": "San_pham", "dtype": "TEXT"},
            {"name": "So_luong", "dtype": "INTEGER"},
            {"name": "Gia", "dtype": "REAL"},
            {"name": "Nha_cung_cap", "dtype": "TEXT"},
        ]

    def test_edu_tin_credit(self):
        """'nhiều tín nhất' → TC should be found"""
        cols = _resolve_column("môn có nhiều tín nhất", self.edu_schema)
        self.assertIsNotNone(cols)
        self.assertIn("TC", cols)

    def test_edu_diem(self):
        """'điểm cao nhất' → no numeric score column → fallback all numeric"""
        cols = _resolve_column("điểm cao nhất", self.edu_schema)
        self.assertIsNotNone(cols)
        # Should return first numeric columns
        self.assertTrue(any(c in cols for c in ["TC", "LT", "TH"]))

    def test_inv_gia(self):
        """'giá cao nhất' → Gia should be found"""
        cols = _resolve_column("giá cao nhất", self.inv_schema)
        self.assertIsNotNone(cols)
        self.assertIn("Gia", cols)

    def test_inv_generic(self):
        """'cái nào cao nhất' → no match → fallback all numeric"""
        cols = _resolve_column("cái nào cao nhất", self.inv_schema)
        self.assertIsNotNone(cols)
        # Should return numeric columns (So_luong, Gia)
        self.assertEqual(len(cols), 2)

    def test_no_numeric(self):
        """No numeric columns → None"""
        schema = [{"name": "Name", "dtype": "TEXT"}]
        self.assertIsNone(_resolve_column("cao nhất", schema))

    def test_partial_match(self):
        """'mã hp' partial match → should find Ma_HP but it's TEXT, so not returned"""
        # Ma_HP is TEXT, so it won't be in numeric cols
        schema = [{"name": "Ma_HP", "dtype": "TEXT"}, {"name": "Diem", "dtype": "REAL"}]
        cols = _resolve_column("điểm cao nhất", schema)
        self.assertEqual(cols, ["Diem"])

    def test_ambiguous_question(self):
        """'nhiều nhất' alone → fallback all numeric"""
        schema = [{"name": "A", "dtype": "INTEGER"}, {"name": "B", "dtype": "REAL"}]
        cols = _resolve_column("cái nào nhiều nhất", schema)
        self.assertEqual(len(cols), 2)


class TestSqlFixer(unittest.TestCase):
    """Test SQL post-processing."""

    def setUp(self):
        self.schema = [
            {"name": "Ma_HP", "dtype": "TEXT"},
            {"name": "Mon", "dtype": "TEXT"},
            {"name": "TC", "dtype": "INTEGER"},
        ]
        self.fixer = SqlFixer(self.schema)

    def test_fix_like_to_ilike(self):
        """Replace LIKE with ILIKE"""
        fixed = self.fixer.fix('SELECT * FROM "t" WHERE "Ma_HP" LIKE \'%a%\'')
        self.assertIn("ILIKE", fixed)
        self.assertNotIn(" LIKE ", fixed)

    def test_fix_column_case(self):
        """Fix wrong case in column name"""
        sql = 'SELECT MAX("ma_hp") FROM "t"'
        fixed = self.fixer.fix(sql)
        self.assertIn('"Ma_HP"', fixed)

    def test_fix_column_no_quotes(self):
        """Fix unquoted column name"""
        sql = "SELECT MAX(tc) FROM \"t\""
        fixed = self.fixer.fix(sql)
        self.assertIn('"TC"', fixed)

    def test_add_limit_select_star(self):
        """Add LIMIT for SELECT *"""
        sql = 'SELECT * FROM "t" WHERE "Ma_HP" ILIKE \'%a%\''
        fixed = self.fixer.fix(sql)
        self.assertIn("LIMIT", fixed.upper())

    def test_no_limit_for_aggregation(self):
        """Don't add LIMIT for COUNT()"""
        sql = 'SELECT COUNT(*) FROM "t"'
        fixed = self.fixer.fix(sql)
        self.assertNotIn("LIMIT", fixed.upper())

    def test_forbidden_drop(self):
        """DROP should raise ValueError"""
        sql = 'DROP TABLE "t"'
        with self.assertRaises(ValueError):
            self.fixer.fix(sql)

    def test_forbidden_delete(self):
        """DELETE should raise ValueError"""
        sql = 'DELETE FROM "t"'
        with self.assertRaises(ValueError):
            self.fixer.fix(sql)

    def test_non_select(self):
        """Non-SELECT should raise ValueError"""
        sql = "INSERT INTO t VALUES (1)"
        with self.assertRaises(ValueError):
            self.fixer.fix(sql)

    def test_preserve_valid_sql(self):
        """Valid SQL should not be modified unnecessarily"""
        sql = 'SELECT MAX("TC") FROM "t"'
        fixed = self.fixer.fix(sql)
        self.assertEqual(fixed, sql)

    def test_fix_columns_preserves_string_literal(self):
        """Column name inside ILIKE string literal must not be corrupted."""
        sql = 'SELECT * FROM "t" WHERE "Mon" ILIKE \'%TC%\''
        fixed = self.fixer.fix(sql)
        self.assertIn("'%TC%'", fixed)


class TestExcelQueryService(unittest.TestCase):
    """Test the main service orchestration."""

    def setUp(self):
        self.service = ExcelQueryService()
        self.mock_db = MagicMock()

        self.mock_table = MagicMock()
        self.mock_table.table_name = "etbl_test_sheet"
        self.mock_table.sheet_name = "Sheet1"
        self.mock_table.column_schema = json.dumps([
            {"name": "Ma_HP", "dtype": "TEXT"},
            {"name": "Mon", "dtype": "TEXT"},
            {"name": "TC", "dtype": "INTEGER"},
            {"name": "LT", "dtype": "INTEGER"},
        ])
        self.mock_table.sample_data = json.dumps([
            {"Ma_HP": "INT2213 1", "Mon": "Chủ nghĩa xã hội KH", "TC": 3, "LT": 2},
            {"Ma_HP": "INT2201 1", "Mon": "Triết học Mác-Lênin", "TC": 3, "LT": 3},
            {"Ma_HP": "INT2204 2", "Mon": "Kinh tế chính trị", "TC": 2, "LT": 2},
        ])
        self.mock_table.row_count = 1775

    def test_extract_keywords_integration(self):
        """Integration: extract keywords from real question"""
        kw = _extract_keywords("cho tôi biết về int2213")
        self.assertEqual(kw, ["int2213"])

    def test_classify_intent_integration(self):
        """Integration: classify real question"""
        kw = _extract_keywords("có bao nhiêu môn")
        intent = _classify_intent("có bao nhiêu môn", kw)
        self.assertEqual(intent, Intent.COUNT)

    def test_build_lookup_sql(self):
        """Build LOOKUP SQL with keywords"""
        schema = json.loads(self.mock_table.column_schema)
        sql = self.service._build_lookup_sql(
            self.mock_table, schema, ["int2213"]
        )
        self.assertIn("search_text", sql)
        self.assertIn("ILIKE ALL", sql)
        self.assertIn("%int2213%", sql)
        self.assertIn(self.mock_table.table_name, sql)

    def test_build_count_sql_no_keywords(self):
        """Build COUNT SQL without keywords"""
        schema = json.loads(self.mock_table.column_schema)
        sql = self.service._build_count_sql(self.mock_table, schema, [])
        self.assertIn("COUNT(*)", sql)
        self.assertNotIn("WHERE", sql.upper())

    def test_build_count_sql_with_keywords(self):
        """Build COUNT SQL with keywords"""
        schema = json.loads(self.mock_table.column_schema)
        sql = self.service._build_count_sql(
            self.mock_table, schema, ["tiếng", "anh"]
        )
        self.assertIn("ILIKE ALL", sql)
        self.assertIn("%tiếng%", sql)

    def test_build_aggr_sql(self):
        """Build MAX SQL"""
        schema = json.loads(self.mock_table.column_schema)
        sql = self.service._build_aggr_sql(
            Intent.MAX, ["TC"], self.mock_table, schema, []
        )
        self.assertIn('MAX("TC")', sql)

    def test_format_result(self):
        """Format query result as markdown"""
        rows = [
            ("INT2213 1", "Chủ nghĩa xã hội KH", 3, 2),
            ("INT2201 1", "Triết học Mác-Lênin", 3, 3),
        ]
        col_keys = ["Ma_HP", "Mon", "TC", "LT"]
        result = self.service._format_result((rows, col_keys))
        self.assertIn("Ma_HP", result)
        self.assertIn("INT2213 1", result)
        self.assertIn("Triết học", result)

    def test_format_empty_result(self):
        """Empty result should return appropriate message"""
        result = self.service._format_result(([], ["Ma_HP"]))
        self.assertEqual(result, "Không có kết quả phù hợp.")

    def test_run_analysis(self):
        """Analysis should execute multiple queries and return formatted result."""
        call_log: list[str] = []

        def mock_execute(sql: str, db):
            call_log.append(sql[:60])
            if "COUNT" in sql:
                return ([(1775,)], ["Total"])
            if "DISTINCT" in sql:
                return ([("CNXH KH",), ("Triết học",)], [sql.split('"')[1]])
            if "MIN" in sql or "MAX" in sql or "AVG" in sql:
                # MIN/MAX/AVG for TC, LT, TH = 9 values
                return ([(2, 5, 3.1, 1, 4, 2.2, 0, 2, 1.0)],
                        ["TC_min", "TC_max", "TC_avg", "LT_min", "LT_max", "LT_avg", "TH_min", "TH_max", "TH_avg"])
            if "LIMIT 5" in sql:
                return (
                    [("INT2213 1", "CNXH KH", 3, 2, 1, "search_text_here")],
                    ["_row_idx", "Ma_HP", "Mon", "TC", "LT", "search_text"]
                )
            return None

        self.service._execute = mock_execute
        result = self.service._run_analysis([self.mock_table], self.mock_db)
        self.assertIn("Sheet1", result)
        self.assertIn("1775", result)
        self.assertGreaterEqual(len(call_log), 4)

    def test_build_lookup_sql_without_search_text(self):
        """Fallback: Build LOOKUP SQL when search_text column doesn't exist"""
        schema = json.loads(self.mock_table.column_schema)
        # Remove search_text from schema
        schema = [c for c in schema if c['name'] != 'search_text']
        sql = self.service._build_lookup_sql(
            self.mock_table, schema, ["int2213"]
        )
        self.assertNotIn("search_text", sql)
        self.assertIn("ILIKE", sql)
        self.assertIn("%int2213%", sql)
        self.assertIn("Mon", sql)  # Should search in TEXT columns like Mon

    def test_build_count_sql_without_search_text(self):
        """Fallback: Build COUNT SQL when search_text column doesn't exist"""
        schema = json.loads(self.mock_table.column_schema)
        # Remove search_text from schema
        schema = [c for c in schema if c['name'] != 'search_text']
        sql = self.service._build_count_sql(
            self.mock_table, schema, ["tiếng", "anh"]
        )
        self.assertNotIn("search_text", sql)
        self.assertIn("ILIKE", sql)
        self.assertIn("%tiếng%", sql)
        self.assertIn("Mon", sql)  # Should search in TEXT columns

    def test_build_aggr_sql_without_search_text(self):
        """Fallback: Build MAX SQL when search_text column doesn't exist"""
        schema = json.loads(self.mock_table.column_schema)
        # Remove search_text from schema
        schema = [c for c in schema if c['name'] != 'search_text']
        sql = self.service._build_aggr_sql(
            Intent.MAX, ["TC"], self.mock_table, schema, ["tiếng", "anh"]
        )
        self.assertNotIn("search_text", sql)
        self.assertIn('MAX("TC")', sql)
        self.assertIn("ILIKE", sql)
        self.assertIn("%tiếng%", sql)


if __name__ == "__main__":
    unittest.main()
