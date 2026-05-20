from __future__ import annotations

from langchain_huggingface import HuggingFaceEmbeddings

<<<<<<< HEAD
from config import Config
=======
try:
    from ..config import Config
except ImportError:  # pragma: no cover
    from config import Config
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca


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
<<<<<<< HEAD
    )
=======
    )
>>>>>>> 9b192d1d56a53f6a50359f035495dbb7c35b64ca
