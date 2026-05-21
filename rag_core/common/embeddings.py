from __future__ import annotations

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

try:
    from ..config import Config
except ImportError:  # pragma: no cover
    from config import Config


def build_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": Config.DEVICE,
            "trust_remote_code": True,
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


@lru_cache(maxsize=4)
def get_embeddings(model_name: str | None = None, device: str | None = None) -> HuggingFaceEmbeddings:
    effective_model = (model_name or Config.EMBEDDING_MODEL_NAME).strip()
    effective_device = (device or Config.DEVICE).strip()
    return HuggingFaceEmbeddings(
        model_name=effective_model,
        model_kwargs={
            "device": effective_device,
            "trust_remote_code": True,
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )
