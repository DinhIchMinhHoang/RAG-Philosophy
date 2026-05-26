from __future__ import annotations

import unittest
from pathlib import Path


class RemoteEmbeddingContractTests(unittest.TestCase):
    def test_backend_runtime_no_longer_imports_local_embedding_model(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        runtime_files = [
            repo_root / "backend" / "app" / "services" / "chat_runtime.py",
            repo_root / "backend" / "app" / "ingest" / "processor.py",
        ]
        forbidden = [
            "rag_core.common.embeddings",
            "SentenceTransformer",
            "sentence_transformers",
            "HuggingFaceEmbeddings",
            "langchain_huggingface",
        ]

        for path in runtime_files:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{path} should use the remote embedding service")
