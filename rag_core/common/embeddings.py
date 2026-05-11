from __future__ import annotations

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
