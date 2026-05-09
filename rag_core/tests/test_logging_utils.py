import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import unittest

from common.logging_utils import configure_logging, get_logger


class TestLoggingUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.root = logging.getLogger()
        self.old_handlers = list(self.root.handlers)
        self.old_level = self.root.level
        for handler in self.old_handlers:
            self.root.removeHandler(handler)
        if hasattr(self.root, "_rag_configured"):
            delattr(self.root, "_rag_configured")

    def tearDown(self) -> None:
        for handler in list(self.root.handlers):
            self.root.removeHandler(handler)
        for handler in self.old_handlers:
            self.root.addHandler(handler)
        self.root.setLevel(self.old_level)
        if hasattr(self.root, "_rag_configured"):
            delattr(self.root, "_rag_configured")

    def test_configure_logging_idempotent(self) -> None:
        configure_logging()
        self.assertTrue(getattr(self.root, "_rag_configured", False))
        self.assertEqual(len(self.root.handlers), 1)

        configure_logging()
        self.assertEqual(len(self.root.handlers), 1)

    def test_get_logger_name(self) -> None:
        logger = get_logger("rag_core.test")
        self.assertEqual(logger.name, "rag_core.test")
