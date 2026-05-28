import sys
import unittest
from pathlib import Path
from unittest.mock import patch

RAG_CORE_DIR = Path(__file__).resolve().parents[1]
if str(RAG_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_CORE_DIR))

import ragas_eval  # noqa: E402
from config import Config  # noqa: E402


class TestRagasEval(unittest.TestCase):
    def setUp(self) -> None:
        self._original_device = Config.DEVICE
        self._original_opencode_key = Config.OPENCODE_API_KEY
        self._original_opencode_base = Config.OPENCODE_API_BASE

    def tearDown(self) -> None:
        Config.DEVICE = self._original_device
        Config.OPENCODE_API_KEY = self._original_opencode_key
        Config.OPENCODE_API_BASE = self._original_opencode_base

    @patch("ragas_eval.torch.cuda.is_available", return_value=True)
    def test_auto_embedding_device_resolves_to_cuda_for_eval(self, _cuda_available) -> None:
        Config.DEVICE = "auto"

        self.assertEqual(ragas_eval._resolve_eval_embedding_device(), "cuda")

    @patch("ragas_eval.torch.cuda.is_available", return_value=False)
    def test_auto_embedding_device_fails_without_cuda_for_eval(self, _cuda_available) -> None:
        Config.DEVICE = "auto"

        with self.assertRaisesRegex(RuntimeError, "could not resolve to CUDA"):
            ragas_eval._resolve_eval_embedding_device()

    @patch("ragas_eval._resolve_eval_embedding_device", return_value="cuda")
    @patch("ragas_eval.get_embeddings", return_value="embeddings")
    def test_build_embeddings_uses_resolved_eval_device(self, get_embeddings, _resolve_device) -> None:
        self.assertEqual(ragas_eval._build_embeddings(), "embeddings")
        get_embeddings.assert_called_once_with(model_name=Config.EMBEDDING_MODEL_NAME, device="cuda")

    @patch("ragas_eval.ChatOpenAI", return_value="llm")
    def test_build_llm_uses_deepseek_flash_for_eval(self, chat_openai) -> None:
        Config.OPENCODE_API_KEY = "opencode-key"
        Config.OPENCODE_API_BASE = "https://opencode.ai/zen/go/v1"

        self.assertEqual(ragas_eval._build_llm(), "llm")
        chat_openai.assert_called_once()
        self.assertEqual(chat_openai.call_args.kwargs["model"], "deepseek-v4-flash")
        self.assertEqual(chat_openai.call_args.kwargs["openai_api_key"], "opencode-key")
        self.assertEqual(chat_openai.call_args.kwargs["openai_api_base"], "https://opencode.ai/zen/go/v1")


if __name__ == "__main__":
    unittest.main()
