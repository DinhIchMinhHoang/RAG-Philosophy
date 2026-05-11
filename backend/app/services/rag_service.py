"""
rag_service.py — Singleton service wrapping the rag_core pipeline.

Responsibilities:
  1. Accept uploaded files, parse them (PDF → Document), chunk, and build
     the vector store + retriever.
  2. Provide a streaming generator that yields answer tokens via
     ChatGoogleGenerativeAI's streaming API.
  3. Maintain an in-memory retriever that is rebuilt whenever new
     documents are ingested.
"""

import os
import sys
import logging
import tempfile
import shutil
from typing import List, AsyncGenerator, Optional
import asyncio

from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ensure rag_core is importable
# ---------------------------------------------------------------------------
_RAG_CORE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # backend/app/services
    "..", "..", "..",                              # project root
    "rag_core",
)
_RAG_CORE_DIR = os.path.normpath(_RAG_CORE_DIR)
if _RAG_CORE_DIR not in sys.path:
    sys.path.insert(0, _RAG_CORE_DIR)

from rag_core.config import Config as RAGConfig           # rag_core/config.py
from rag_core.step1_parser import HybridPDFParser          # rag_core/step1_parser.py
from rag_core.step2_chunker import chunk_documents         # rag_core/step2_chunker.py
from rag_core.step3_vector_db import build_vector_db       # rag_core/step3_vector_db.py

# ---------------------------------------------------------------------------
# System Prompt for the streaming chain (matches step4_generator.py style)
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = (
    "Bạn là chuyên gia AI, trợ lý học tập cho sinh viên "
    "Đại học Công nghệ (UET). Bạn sẽ nhận được các đoạn trích dẫn "
    "từ giáo trình. Hãy trả lời câu hỏi dựa TRỰC TIẾP trên "
    "các đoạn văn được cung cấp dưới đây.\n\n"
    "Quy tắc:\n"
    "1. Chỉ sử dụng thông tin từ tài liệu được cung cấp.\n"
    "2. Nếu thông tin không đủ, hãy chỉ ra phần nào thiếu "
    "thay vì tự ý bổ sung.\n"
    "3. Luôn đính kèm số trang (VD: [Trang X]) vào cuối "
    "mỗi ý quan trọng trong câu trả lời.\n\n"
    "Tài liệu tham khảo:\n"
    "{context}"
)


class RAGService:
    """Singleton-style RAG service for the backend."""

    def __init__(self) -> None:
        self._retriever = None
        self._all_child_docs: List[Document] = []
        self._all_parent_docs: List[Document] = []
        self._source_files: List[str] = []  # filenames of ingested sources
        self._parser = HybridPDFParser()
        self._upload_dir = tempfile.mkdtemp(prefix="rag_uploads_")
        logger.info(f"[RAGService] Upload temp dir: {self._upload_dir}")

    # ------------------------------------------------------------------
    #  Document Ingestion
    # ------------------------------------------------------------------
    def ingest_file(self, filename: str, file_bytes: bytes) -> dict:
        """
        Save uploaded file to disk, parse, chunk, and rebuild the
        vector store.  Returns a summary dict.
        """
        save_path = os.path.join(self._upload_dir, filename)
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        logger.info(f"[RAGService] Ingesting: {filename}")

        # Step 1 — Parse
        pages: List[Document] = self._parser.parse_pdf(save_path)
        if not pages:
            return {"filename": filename, "status": "empty", "pages": 0}

        # Step 2 — Chunk
        child_docs, parent_docs = chunk_documents(pages)
        self._all_child_docs.extend(child_docs)
        self._all_parent_docs.extend(parent_docs)
        self._source_files.append(filename)

        # Step 3 — Rebuild vector DB with ALL documents so far
        self._retriever = build_vector_db(
            self._all_child_docs, self._all_parent_docs
        )

        logger.info(
            f"[RAGService] ✅ {filename}: {len(pages)} pages, "
            f"{len(child_docs)} children, {len(parent_docs)} parents. "
            f"Total sources: {len(self._source_files)}"
        )

        return {
            "filename": filename,
            "status": "ok",
            "pages": len(pages),
            "chunks": len(child_docs),
        }

    # ------------------------------------------------------------------
    #  Query — Streaming
    # ------------------------------------------------------------------
    async def stream_answer(self, question: str) -> AsyncGenerator[str, None]:
        """
        Retrieve relevant documents and stream the LLM answer
        token-by-token using ChatGoogleGenerativeAI.astream().
        Yields plain-text chunks.
        """
        if self._retriever is None:
            yield "⚠️ Chưa có tài liệu nào được tải lên. Vui lòng thêm nguồn trước khi hỏi."
            return

        # Retrieve context documents
        # Retrieval may perform CPU work (BM25) and/or network I/O (Cohere rerank).
        # Run in a worker thread to avoid blocking the event loop.
        docs = await asyncio.to_thread(self._retriever.invoke, question)
        if not docs:
            yield "Không tìm thấy tài liệu phù hợp với câu hỏi của bạn."
            return

        # Format context with source/page info
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "N/A")
            page = doc.metadata.get("page", "N/A")
            context_parts.append(
                f"[Tài liệu {i+1} — {source}, Trang {page}]\n"
                f"{doc.page_content}"
            )
        context_text = "\n\n---\n\n".join(context_parts)

        # Build streaming LLM chain
        llm = ChatGoogleGenerativeAI(
            model=RAGConfig.LLM_MODEL,
            temperature=0.2,
            google_api_key=RAGConfig.GEMINI_API_KEY,
            # streaming=True,  # astream() sẽ tự động bật streaming mode
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", _SYSTEM_PROMPT),
            ("human", "{input}"),
        ])

        # Simple chain: prompt → LLM → string output
        chain = prompt | llm | StrOutputParser()

        # Stream tokens
        async for chunk in chain.astream({
            "context": context_text,
            "input": question,
        }):
            yield chunk

        # Append sources footer
        sources_footer = "\n\n---\n📚 **Nguồn tham khảo:**\n"
        seen = set()
        for doc in docs:
            source = doc.metadata.get("source", "N/A")
            page = doc.metadata.get("page", "N/A")
            key = f"{source}::{page}"
            if key not in seen:
                seen.add(key)
                sources_footer += f"- {source}, Trang {page}\n"
        yield sources_footer

    # ------------------------------------------------------------------
    #  Status / Reset
    # ------------------------------------------------------------------
    @property
    def has_sources(self) -> bool:
        return self._retriever is not None

    @property
    def source_count(self) -> int:
        return len(self._source_files)

    @property
    def sources(self) -> List[str]:
        return list(self._source_files)

    def reset(self) -> None:
        """Clear all ingested documents and reset the retriever."""
        self._retriever = None
        self._all_child_docs.clear()
        self._all_parent_docs.clear()
        self._source_files.clear()
        # Clean temp directory
        if os.path.exists(self._upload_dir):
            shutil.rmtree(self._upload_dir, ignore_errors=True)
        self._upload_dir = tempfile.mkdtemp(prefix="rag_uploads_")
        logger.info("[RAGService] Reset complete.")

    def get_page_image(self, filename: str, page_number: int) -> Optional[bytes]:
        """
        Render a specific page of a PDF file to PNG bytes.
        page_number is 1-indexed.
        """
        import fitz
        file_path = os.path.join(self._upload_dir, filename)
        if not os.path.exists(file_path):
            logger.warning(f"[RAGService] File not found: {file_path}")
            return None

        try:
            doc = fitz.open(file_path)
            # fitz is 0-indexed
            page_idx = page_number - 1
            if page_idx < 0 or page_idx >= doc.page_count:
                doc.close()
                return None
            
            page = doc[page_idx]
            # Higher DPI for better quality
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            doc.close()
            return img_bytes
        except Exception as e:
            logger.error(f"[RAGService] Error rendering page {page_number} of {filename}: {e}")
            return None


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
rag_service = RAGService()
