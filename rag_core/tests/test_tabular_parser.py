"""
rag_core/tests/test_tabular_parser.py

Unit tests for TabularParser V3 FINAL.
Tests: wide table fallback, CSV streaming, merged cells, citation contract, etc.
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestTabularParserImports(unittest.TestCase):
    """Test that all imports work."""
    
    def test_import_tabular_parser(self):
        """TabularParser should be importable."""
        try:
            from rag_core.parsers.tabular_parser import TabularParser, MemoryGuard
            self.assertIsNotNone(TabularParser)
            self.assertIsNotNone(MemoryGuard)
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_import_parser_registry(self):
        """ParserRegistry should be importable."""
        try:
            from rag_core.parsers import ParserRegistry, parser_registry
            self.assertIsNotNone(ParserRegistry)
            self.assertIsNotNone(parser_registry)
        except ImportError as e:
            self.fail(f"Import failed: {e}")


class TestTabularParserBasic(unittest.TestCase):
    """Basic functionality tests."""
    
    @classmethod
    def setUpClass(cls):
        """Check if fixtures exist."""
        if not FIXTURES_DIR.exists():
            unittest.skip("Fixtures directory not found. Run generate_fixtures.py first.")
        
        # Check for at least one fixture
        fixtures = list(FIXTURES_DIR.glob("*"))
        if not fixtures:
            unittest.skip("No fixture files found. Run generate_fixtures.py first.")
    
    def test_config_loading(self):
        """Config should have TABULAR settings."""
        try:
            from rag_core.config import Config
            self.assertTrue(hasattr(Config, 'TABULAR_CHUNK_ROWS'))
            self.assertTrue(hasattr(Config, 'TABULAR_MAX_COLS'))
            self.assertTrue(hasattr(Config, 'MAX_TABULAR_SIZE_MB'))
        except ImportError:
            self.fail("Could not import Config")
    
    def test_parser_registry_detect(self):
        """ParserRegistry should detect file formats."""
        from rag_core.parsers import ParserRegistry
        registry = ParserRegistry()
        
        self.assertEqual(registry.get_parser_type("test.pdf"), "pdf")
        self.assertEqual(registry.get_parser_type("test.xlsx"), "tabular")
        self.assertEqual(registry.get_parser_type("test.xls"), "tabular")
        self.assertEqual(registry.get_parser_type("test.csv"), "tabular")
        self.assertEqual(registry.get_parser_type("test.docx"), "unknown")
    
    def test_tabular_parser_initialization(self):
        """TabularParser should initialize with defaults."""
        from rag_core.parsers.tabular_parser import TabularParser
        
        parser = TabularParser()
        self.assertEqual(parser.max_rows, 50)  # Default
        self.assertEqual(parser.max_cols, 15)   # Default
        self.assertEqual(parser.max_size_mb, 20)  # Default
    
    def test_tabular_parser_custom_params(self):
        """TabularParser should accept custom params."""
        from rag_core.parsers.tabular_parser import TabularParser
        
        parser = TabularParser(max_rows=100, max_cols=10, max_size_mb=30)
        self.assertEqual(parser.max_rows, 100)
        self.assertEqual(parser.max_cols, 10)
        self.assertEqual(parser.max_size_mb, 30)


class TestCitationContract(unittest.TestCase):
    """Test Citation Contract compliance."""
    
    @classmethod
    def setUpClass(cls):
        if not FIXTURES_DIR.exists():
            unittest.skip("Fixtures directory not found")
    
    def test_csv_metadata_has_page(self):
        """CSV documents must have page metadata."""
        csv_file = FIXTURES_DIR / "normal_table_10cols.xlsx"
        if not csv_file.exists():
            csv_file = FIXTURES_DIR / "large_csv_10k.csv"
        
        if not csv_file.exists():
            unittest.skip("No CSV fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser(max_rows=10)  # Small chunks
        
        docs = parser.parse(str(csv_file))
        
        self.assertGreater(len(docs), 0)
        for doc in docs:
            self.assertIn('page', doc.metadata)
            self.assertIsInstance(doc.metadata['page'], int)
    
    def test_excel_sheets_have_sequential_pages(self):
        """Excel sheets should have distinct page numbers for different sheets."""
        xlsx_file = FIXTURES_DIR / "normal_table_10cols.xlsx"
        if not xlsx_file.exists():
            unittest.skip("No Excel fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser()
        
        docs = parser.parse(str(xlsx_file))
        
        # All docs should have page metadata
        self.assertGreater(len(docs), 0)
        for doc in docs:
            self.assertIn('page', doc.metadata)
            self.assertIsInstance(doc.metadata['page'], int)
            self.assertGreater(doc.metadata['page'], 0)
        
        # Each chunk gets a sequential page number
        pages = [doc.metadata['page'] for doc in docs]
        self.assertEqual(pages[0], 1, "First chunk should have page=1")
        self.assertEqual(pages, sorted(pages), "Pages should be sequential")


class TestWideTableFallback(unittest.TestCase):
    """Test wide table detection and Key-Value fallback."""
    
    @classmethod
    def setUpClass(cls):
        if not FIXTURES_DIR.exists():
            unittest.skip("Fixtures directory not found")
    
    def test_wide_table_uses_key_value(self):
        """Table with >15 cols should use Key-Value format."""
        wide_file = FIXTURES_DIR / "wide_table_20cols.xlsx"
        if not wide_file.exists():
            unittest.skip("No wide table fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser(max_cols=15)
        
        docs = parser.parse(str(wide_file))
        
        self.assertGreater(len(docs), 0)
        for doc in docs:
            self.assertIn('Key-Value', doc.page_content)
    
    def test_normal_table_uses_markdown(self):
        """Table with <=15 cols should use Markdown format."""
        normal_file = FIXTURES_DIR / "normal_table_10cols.xlsx"
        if not normal_file.exists():
            unittest.skip("No normal table fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser(max_cols=15)
        
        docs = parser.parse(str(normal_file))
        
        self.assertGreater(len(docs), 0)
        for doc in docs:
            self.assertIn('Markdown Table', doc.page_content)
            self.assertIn('|', doc.page_content)  # Markdown table separator


class TestCSVStreaming(unittest.TestCase):
    """Test CSV streaming with correct row offsets."""
    
    @classmethod
    def setUpClass(cls):
        if not FIXTURES_DIR.exists():
            unittest.skip("Fixtures directory not found")
    
    def test_csv_row_ranges_sequential(self):
        """CSV chunks should have correct, sequential row ranges."""
        csv_file = FIXTURES_DIR / "large_csv_10k.csv"
        if not csv_file.exists():
            unittest.skip("No large CSV fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser(max_rows=50)
        
        docs = parser.parse(str(csv_file))
        
        # Check sequential row numbers
        for i, doc in enumerate(docs):
            expected_start = i * 50 + 1
            self.assertIn(f"Rows: {expected_start}", doc.page_content)
    
    def test_csv_page_numbers(self):
        """CSV chunks should have sequential page numbers."""
        csv_file = FIXTURES_DIR / "large_csv_10k.csv"
        if not csv_file.exists():
            unittest.skip("No large CSV fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser(max_rows=50)
        
        docs = parser.parse(str(csv_file))
        
        for i, doc in enumerate(docs):
            self.assertEqual(doc.metadata['page'], i + 1)


class TestChunking(unittest.TestCase):
    """Test row-based chunking."""
    
    @classmethod
    def setUpClass(cls):
        if not FIXTURES_DIR.exists():
            unittest.skip("Fixtures directory not found")
    
    def test_chunk_size_respected(self):
        """Chunk size should be respected (or less for final chunk)."""
        xlsx_file = FIXTURES_DIR / "normal_table_10cols.xlsx"
        if not xlsx_file.exists():
            unittest.skip("No Excel fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser(max_rows=30)  # Small chunks
        
        docs = parser.parse(str(xlsx_file))
        
        self.assertGreater(len(docs), 0)
        # All but last chunk should be <= 30 rows
        for doc in docs[:-1]:
            match = doc.metadata.get('row_range', '0-0')
            start, end = match.split('-')
            row_count = int(end) - int(start) + 1
            self.assertLessEqual(row_count, 30)


class TestMemorySafety(unittest.TestCase):
    """Test memory safety features."""
    
    def test_file_size_validation(self):
        """Parser should reject oversized files."""
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser(max_size_mb=1)  # Very small limit
        
        with self.assertRaises(ValueError):
            # Create a file larger than 1MB in memory
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
                # Write 2MB of data (use 'a' mode to keep file open properly)
                f.write('x' * (2 * 1024 * 1024))
                temp_path = f.name
            
            try:
                parser.parse(temp_path)
            finally:
                # Close any handles before deleting
                import gc
                gc.collect()
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
    
    def test_nonexistent_file_raises(self):
        """Parser should raise error for nonexistent files."""
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser()
        
        with self.assertRaises(FileNotFoundError):
            parser.parse("/nonexistent/path/file.csv")


class TestIsTabularBypass(unittest.TestCase):
    """Test that is_tabular flag is set correctly."""
    
    @classmethod
    def setUpClass(cls):
        if not FIXTURES_DIR.exists():
            unittest.skip("Fixtures directory not found")
    
    def test_tabular_metadata_flag(self):
        """Documents should have is_tabular=True."""
        xlsx_file = FIXTURES_DIR / "normal_table_10cols.xlsx"
        if not xlsx_file.exists():
            unittest.skip("No Excel fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        parser = TabularParser()
        
        docs = parser.parse(str(xlsx_file))
        
        for doc in docs:
            self.assertTrue(doc.metadata.get('is_tabular'))
            self.assertIn('doc_type', doc.metadata)
            self.assertIn('sheet_name', doc.metadata)
            self.assertIn('row_range', doc.metadata)


class TestStep2ChunkerBypass(unittest.TestCase):
    """Test that step2_chunker bypasses tabular data."""
    
    @classmethod
    def setUpClass(cls):
        if not FIXTURES_DIR.exists():
            unittest.skip("Fixtures directory not found")
    
    def test_tabular_not_split_by_parent_splitter(self):
        """Tabular content should not be split by _PARENT_SPLITTER."""
        xlsx_file = FIXTURES_DIR / "normal_table_10cols.xlsx"
        if not xlsx_file.exists():
            unittest.skip("No Excel fixture found")
        
        from rag_core.parsers.tabular_parser import TabularParser
        from rag_core.step2_chunker import chunk_documents
        
        parser = TabularParser()
        parsed = parser.parse(str(xlsx_file))
        
        # Get original content length
        original_lengths = [len(doc.page_content) for doc in parsed]
        
        # Chunk through step2_chunker
        child_docs, parent_docs = chunk_documents(parsed)
        
        # Parent docs should preserve content (not be split further)
        for i, parent in enumerate(parent_docs):
            if i < len(original_lengths):
                # Content should be at least 80% of original (allowing for metadata changes)
                self.assertGreaterEqual(
                    len(parent.page_content),
                    original_lengths[i] * 0.8
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)