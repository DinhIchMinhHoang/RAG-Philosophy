"""
Base chunker interface and token counting utilities.
"""
from abc import ABC, abstractmethod
from typing import List

from .types import Chunk, ChunkingConfig


class TokenCounter(ABC):
    """Abstract token counter."""

    @abstractmethod
    def count(self, text: str) -> int:
        """Count tokens in text."""
        pass


class TikTokenCounter(TokenCounter):
    """Token counter using tiktoken (OpenAI tokenizers)."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize tiktoken counter."""
        try:
            import tiktoken
            self.encoding = tiktoken.get_encoding(encoding_name)
        except ImportError:
            raise ImportError(
                "tiktoken not installed (pip install tiktoken)"
            )

    def count(self, text: str) -> int:
        """Count tokens using tiktoken."""
        return len(self.encoding.encode(text))


class SimpleTokenCounter(TokenCounter):
    """Simple word-based token counter (fallback)."""

    def count(self, text: str) -> int:
        """Count tokens as simple word count."""
        return len(text.split())


class BaseChunker(ABC):
    """Abstract base class for chunkers."""

    def __init__(self, config: ChunkingConfig):
        """Initialize chunker with config."""
        self.config = config
        self.token_counter = self._init_token_counter()

    def _init_token_counter(self) -> TokenCounter:
        """Initialize token counter based on config."""
        if self.config.token_counter_name == "tiktoken":
            try:
                return TikTokenCounter()
            except ImportError:
                return SimpleTokenCounter()
        else:
            return SimpleTokenCounter()

    @abstractmethod
    def chunk(self, text: str, source_path: str = "unknown") -> List[Chunk]:
        """Split text into chunks. Returns list of Chunk objects."""
        pass
