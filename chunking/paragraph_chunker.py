"""
Paragraph-based chunker with Vietnamese sentence splitting and token-aware assembly.
"""
import logging
import re
import hashlib
from typing import List, Tuple, Optional

from .base import BaseChunker
from .types import Chunk, ChunkMetadata, ChunkingConfig

try:
    from underthesea import sent_tokenize
except ImportError:
    sent_tokenize = None

logger = logging.getLogger(__name__)


class ParagraphChunker(BaseChunker):
    """
    Paragraph-based chunker that:
    1. Splits text into paragraphs
    2. For long paragraphs, uses Vietnamese sentence splitting
    3. Assembles chunks with token budget and sliding window overlap
    """

    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize paragraph chunker."""
        if config is None:
            config = ChunkingConfig()
        super().__init__(config)
        logger.info(
            f"Initialized ParagraphChunker: "
            f"max_tokens={config.max_tokens}, "
            f"overlap={config.overlap_tokens}, "
            f"language={config.language}"
        )

    def _extract_paragraphs(self, text: str) -> List[str]:
        """
        Extract paragraphs from text.
        Paragraphs are separated by:
        1. Double newlines (standard paragraph separator)
        2. Single newlines (fallback)
        3. If no newlines exist, split by numbered/bullet points or sentence periods
        """
        # Try double newlines first
        if '\n\n' in text:
            paragraphs = re.split(r"\n\s*\n+", text.strip())
        # Try single newlines if text has them
        elif '\n' in text:
            paragraphs = re.split(r"\n+", text.strip())
        # Fallback: split by sentence-like boundaries (periods, numbers, etc.)
        else:
            # Split on numbered items (1. 2. 3.) or long sentences
            paragraphs = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text.strip())
            if len(paragraphs) <= 1:
                # If still one paragraph, split every ~500 chars for safety
                if len(text) > 1000:
                    paragraphs = [text[i:i+500] for i in range(0, len(text), 500)]
                else:
                    paragraphs = [text]
        
        # Filter out empty paragraphs and strip whitespace
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        logger.debug(f"Extracted {len(paragraphs)} paragraphs")
        return paragraphs

    def _split_paragraph_to_sentences(self, paragraph: str) -> List[str]:
        """
        Split a paragraph into sentences using Vietnamese-aware tokenizer if available.
        Falls back to simple heuristic if underthesea is not available.
        """
        if sent_tokenize:
            try:
                sentences = sent_tokenize(paragraph)
                return [s.strip() for s in sentences if s.strip()]
            except Exception as e:
                logger.warning(f"sent_tokenize failed: {e}. Using fallback.")

        # Fallback: simple regex split on common sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        return [s.strip() for s in sentences if s.strip()]

    def _detect_special_content(self, text: str) -> Tuple[bool, bool]:
        """Detect if text contains code blocks or tables."""
        has_code = bool(re.search(r'```|<code>|    \S', text))
        has_table = bool(re.search(r'\|.*\||\t|\+---', text))
        return has_code, has_table

    def _generate_chunk_id(
        self, source_path: str, chunk_index: int, text: str
    ) -> str:
        """Generate deterministic chunk ID."""
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"{source_path}#{chunk_index}#{content_hash}"

    def chunk(self, text: str, source_path: str = "unknown") -> List[Chunk]:
        """
        Chunk text into semantic chunks with token budgets.

        Args:
            text: Full text to chunk
            source_path: Original source file path (for metadata)

        Returns:
            List of Chunk objects
        """
        logger.info(f"Chunking {len(text)} chars from {source_path}")

        # Extract paragraphs
        logger.debug("Extracting paragraphs...")
        paragraphs = self._extract_paragraphs(text)
        if not paragraphs:
            logger.warning(f"No paragraphs extracted from {source_path}")
            return []
        
        logger.info(f"  Extracted {len(paragraphs)} paragraphs")

        # Prepare list of sentence groups (each para broken into sentences)
        logger.debug("Tokenizing paragraphs into sentences...")
        sentence_groups: List[List[str]] = []
        for para_idx, para in enumerate(paragraphs):
            sentences = self._split_paragraph_to_sentences(para)
            if sentences:
                sentence_groups.append(sentences)
            if (para_idx + 1) % 10 == 0:
                logger.debug(f"  Processed {para_idx + 1}/{len(paragraphs)} paragraphs")
        
        logger.info(f"  Created {len(sentence_groups)} groups of sentences")

        # Assemble chunks using sliding window with overlap
        logger.debug("Assembling chunks with token budget...")
        chunks: List[Chunk] = []
        chunk_index = 0

        i = 0
        while i < len(sentence_groups):
            # Assemble chunk starting from sentence group i
            chunk_text_parts: List[str] = []
            chunk_token_count = 0
            start_group_idx = i
            end_group_idx = i

            # Greedily add sentence groups until token budget exceeded
            while end_group_idx < len(sentence_groups):
                para_text = " ".join(sentence_groups[end_group_idx])
                para_tokens = self.token_counter.count(para_text)

                # Check if adding this paragraph would exceed budget
                tentative_count = chunk_token_count + para_tokens
                if (
                    tentative_count <= self.config.max_tokens
                    or chunk_token_count == 0  # at least one paragraph per chunk
                ):
                    chunk_text_parts.append(para_text)
                    chunk_token_count = tentative_count
                    end_group_idx += 1
                else:
                    break

            if not chunk_text_parts:
                logger.warning(f"Paragraph {i} exceeds max_tokens. Skipping.")
                i += 1
                continue

            # Create chunk
            chunk_text = " ".join(chunk_text_parts)
            
            # Skip if too small (below min_tokens)
            if chunk_token_count < self.config.min_tokens:
                logger.debug(
                    f"Skipping chunk {chunk_index}: only {chunk_token_count} tokens"
                )
                i = end_group_idx
                continue

            # Detect special content
            has_code, has_table = self._detect_special_content(chunk_text)

            # Create metadata
            chunk_id = self._generate_chunk_id(source_path, chunk_index, chunk_text)
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                source_path=source_path,
                source_type=source_path.split(".")[-1] if "." in source_path else "txt",
                chunk_index=chunk_index,
                total_chunks=0,  # Will be set later
                paragraph_index=start_group_idx,
                token_count=chunk_token_count,
                language=self.config.language,
                has_code=has_code,
                has_table=has_table,
            )

            chunk = Chunk(text=chunk_text, metadata=metadata)
            chunks.append(chunk)

            chunk_index += 1
            
            if chunk_index % 5 == 0:
                logger.debug(f"  Created {chunk_index} chunks so far...")

            # Move offset: step forward so that only ~overlap_tokens worth of
            # trailing paragraph groups are re-included in the next chunk.
            if self.config.overlap_tokens > 0 and end_group_idx < len(sentence_groups):
                overlap_token_budget = self.config.overlap_tokens
                overlap_paras = 0
                accumulated = 0
                # Walk backward from the end of the current chunk
                for g in range(end_group_idx - 1, start_group_idx - 1, -1):
                    para_text = " ".join(sentence_groups[g])
                    accumulated += self.token_counter.count(para_text)
                    overlap_paras += 1
                    if accumulated >= overlap_token_budget:
                        break
                # Ensure we advance by at least 1 group to avoid infinite loop
                i = max(start_group_idx + 1, end_group_idx - overlap_paras)
            else:
                # No overlap requested or last chunk — move to end
                i = end_group_idx

        # Update total_chunks count
        for i, chunk in enumerate(chunks):
            chunk.metadata.total_chunks = len(chunks)

        logger.info(
            f"Created {len(chunks)} chunks from {len(paragraphs)} paragraphs "
            f"({source_path})"
        )
        return chunks

    def chunk_from_jsonl(
        self, jsonl_file: str, output_jsonl: Optional[str] = None
    ) -> List[Chunk]:
        """
        Chunk conversions from JSONL file (output of converter module).

        Args:
            jsonl_file: JSONL file path (from converter output)
            output_jsonl: Optional output JSONL path

        Returns:
            List of all chunks
        """
        import json
        from pathlib import Path

        all_chunks: List[Chunk] = []

        logger.info(f"Processing conversions from {jsonl_file}")

        # Count total lines first for progress bar
        total_lines = 0
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    total_lines += 1
        
        logger.info(f"Found {total_lines} conversions to process")

        # Process each line
        line_idx = 0
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                line_idx += 1
                
                if not line.strip():
                    continue

                try:
                    conv_data = json.loads(line)
                    text = conv_data.get("text", "")
                    metadata = conv_data.get("metadata", {})
                    source_path = metadata.get("source_path", "unknown")

                    if not text:
                        logger.warning(f"Empty text at line {line_idx}, skipping")
                        continue

                    logger.info(f"Line {line_idx}: chunking {len(text)} chars")
                    chunks = self.chunk(text, source_path=source_path)
                    logger.info(f"Line {line_idx}: created {len(chunks)} chunks")
                    
                    all_chunks.extend(chunks)

                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error at line {line_idx}: {e}")
                except Exception as e:
                    logger.error(f"Error processing line {line_idx}: {e}")
                    import traceback
                    traceback.print_exc()

        logger.info(f"Total chunks created: {len(all_chunks)}")
        
        # Save output if requested
        if output_jsonl:
            output_path = Path(output_jsonl)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                for chunk in all_chunks:
                    f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
            logger.info(f"Saved {len(all_chunks)} chunks to {output_jsonl}")

        return all_chunks
