from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

try:
    from ..config import DEFAULT_LLM_MODEL, Config
except ImportError:  # pragma: no cover
    from config import DEFAULT_LLM_MODEL, Config


def resolve_llm_model(model: str | None = None) -> str:
    selected_model = (model if model is not None else Config.LLM_MODEL) or DEFAULT_LLM_MODEL
    selected_model = selected_model.strip()
    return selected_model or DEFAULT_LLM_MODEL


def infer_llm_provider(model: str | None = None, provider: str | None = None) -> str:
    """Resolve which chat API should serve the configured model."""
    selected_provider = (provider or Config.LLM_PROVIDER or "auto").strip().lower()
    if selected_provider in {"gemini", "opencode"}:
        return selected_provider
    if selected_provider != "auto":
        raise ValueError(f"Unsupported LLM_PROVIDER: {selected_provider}")

    selected_model = resolve_llm_model(model).lower()
    if selected_model.startswith("gemini"):
        return "gemini"
    return "opencode"


def build_chat_llm(*, model: str | None = None, temperature: float = 0.2, provider: str | None = None):
    selected_model = resolve_llm_model(model)

    selected_provider = infer_llm_provider(selected_model, provider)
    if selected_provider == "gemini":
        if not Config.GEMINI_API_KEY:
            raise EnvironmentError("GEMINI_API_KEY is not set.")
        return ChatGoogleGenerativeAI(
            model=selected_model,
            temperature=temperature,
            google_api_key=Config.GEMINI_API_KEY,
        )

    if not Config.OPENCODE_API_KEY:
        raise EnvironmentError("OPENCODE_API_KEY is not set.")
    return ChatOpenAI(
        model=selected_model,
        temperature=temperature,
        openai_api_key=Config.OPENCODE_API_KEY,
        openai_api_base=Config.OPENCODE_API_BASE,
    )
