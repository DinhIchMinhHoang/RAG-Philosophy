"""
Types and data classes for chunking module.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class ChunkMetadata:
    """Metadata about a chunk."""
    chunk_id: str
    source_path: str  # original source file
    source_type: str  # txt, docx, pdf, etc.
    chunk_index: int
    total_chunks: int
    
    # Text positioning
    paragraph_index: Optional[int] = None
    sentence_range: Optional[tuple[int, int]] = None  # (start_sent_idx, end_sent_idx)
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    
    # Token info
    token_count: int = 0
    page_index: Optional[int] = None
    
    # Language and content
    language: str = "vi"
    has_code: bool = False
    has_table: bool = False
    
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    """A chunk of text with metadata."""
    text: str
    metadata: ChunkMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "metadata": {
                "chunk_id": self.metadata.chunk_id,
                "source_path": self.metadata.source_path,
                "source_type": self.metadata.source_type,
                "chunk_index": self.metadata.chunk_index,
                "total_chunks": self.metadata.total_chunks,
                "paragraph_index": self.metadata.paragraph_index,
                "sentence_range": self.metadata.sentence_range,
                "char_start": self.metadata.char_start,
                "char_end": self.metadata.char_end,
                "token_count": self.metadata.token_count,
                "page_index": self.metadata.page_index,
                "language": self.metadata.language,
                "has_code": self.metadata.has_code,
                "has_table": self.metadata.has_table,
                "extra": self.metadata.extra,
            }
        }


@dataclass
class ChunkingConfig:
    """Configuration for chunking."""
    max_tokens: int = 500
    min_tokens: int = 50
    overlap_tokens: int = 50
    language: str = "vi"
    
    # Special handling flags
    preserve_code_blocks: bool = True
    preserve_tables: bool = True
    merge_short_paras: bool = True
    remove_boilerplate: bool = False
    
    # Token counter (default: tiktoken)
    token_counter_name: str = "tiktoken"
