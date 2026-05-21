import unittest
from unittest.mock import patch

from rag_core.common import llm
from rag_core.config import Config


class TestLLMFactory(unittest.TestCase):
    def setUp(self) -> None:
        self._original_model = Config.LLM_MODEL
        self._original_provider = Config.LLM_PROVIDER
        self._original_gemini_key = Config.GEMINI_API_KEY
        self._original_opencode_key = Config.OPENCODE_API_KEY
        self._original_opencode_base = Config.OPENCODE_API_BASE

    def tearDown(self) -> None:
        Config.LLM_MODEL = self._original_model
        Config.LLM_PROVIDER = self._original_provider
        Config.GEMINI_API_KEY = self._original_gemini_key
        Config.OPENCODE_API_KEY = self._original_opencode_key
        Config.OPENCODE_API_BASE = self._original_opencode_base

    def test_infer_provider_from_model_name(self) -> None:
        Config.LLM_PROVIDER = "auto"

        self.assertEqual(llm.infer_llm_provider("gemini-3.1-flash-lite-preview"), "gemini")
        self.assertEqual(llm.infer_llm_provider("deepseek-v4-flash"), "opencode")

    def test_missing_model_uses_default_instead_of_crashing(self) -> None:
        Config.LLM_MODEL = None
        Config.LLM_PROVIDER = "auto"
        Config.GEMINI_API_KEY = "gemini-key"

        with patch("rag_core.common.llm.ChatGoogleGenerativeAI", return_value="gemini-client") as client:
            result = llm.build_chat_llm()

        self.assertEqual(result, "gemini-client")
        self.assertEqual(client.call_args.kwargs["model"], llm.DEFAULT_LLM_MODEL)

    def test_builds_gemini_client_for_gemini_model(self) -> None:
        Config.LLM_PROVIDER = "auto"
        Config.GEMINI_API_KEY = "gemini-key"

        with patch("rag_core.common.llm.ChatGoogleGenerativeAI", return_value="gemini-client") as client:
            result = llm.build_chat_llm(model="gemini-3.1-flash-lite-preview")

        self.assertEqual(result, "gemini-client")
        client.assert_called_once()
        self.assertEqual(client.call_args.kwargs["model"], "gemini-3.1-flash-lite-preview")
        self.assertEqual(client.call_args.kwargs["google_api_key"], "gemini-key")

    def test_builds_opencode_client_for_non_gemini_model(self) -> None:
        Config.LLM_PROVIDER = "auto"
        Config.OPENCODE_API_KEY = "opencode-key"
        Config.OPENCODE_API_BASE = "https://opencode.ai/zen/go/v1"

        with patch("rag_core.common.llm.ChatOpenAI", return_value="opencode-client") as client:
            result = llm.build_chat_llm(model="deepseek-v4-flash")

        self.assertEqual(result, "opencode-client")
        client.assert_called_once()
        self.assertEqual(client.call_args.kwargs["model"], "deepseek-v4-flash")
        self.assertEqual(client.call_args.kwargs["openai_api_key"], "opencode-key")
        self.assertEqual(client.call_args.kwargs["openai_api_base"], "https://opencode.ai/zen/go/v1")


if __name__ == "__main__":
    unittest.main()
