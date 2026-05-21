from __future__ import annotations

import logging
from dataclasses import dataclass

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client.http import models as rest
from sqlalchemy.orm import Session

from ..core.settings import settings
from ..ingest.qdrant_store import build_qdrant_client
from ..models import DocumentChunk

try:
    from rag_core.common.embeddings import build_embeddings as build_embeddings_from_common
    from rag_core.common.llm import build_chat_llm, infer_llm_provider
    from rag_core.config import Config as RagConfig
except Exception as exc:  # pragma: no cover
    raise RuntimeError(f"Failed to load rag_core modules: {exc}") from exc

logger = logging.getLogger(__name__)

_EXCEL_QUERY_SERVICE: "ExcelQueryService | None" = None


def _get_excel_query_service():
    global _EXCEL_QUERY_SERVICE
    if _EXCEL_QUERY_SERVICE is None:
        from .excel_query_service import excel_query_service as _svc
        _EXCEL_QUERY_SERVICE = _svc
    return _EXCEL_QUERY_SERVICE

_SYSTEM_PROMPT = (
    "Bạn là trợ lý AI học tập thân thiện. BẠN PHẢI LUÔN TRẢ LỜI BẰNG TIẾNG VIỆT.\n\n"
    "Quy tắc trả lời:\n"
    "1. Nếu phần 'Context' bên dưới bị TRỐNG:\n"
    "   - Nếu người dùng chào hỏi, hãy chào lại tự nhiên và mời họ tải tài liệu lên.\n"
    "   - Nếu hỏi kiến thức, hãy từ chối lịch sự vì chưa có tài liệu để tra cứu.\n"
    "2. Nếu phần 'Context' CÓ dữ liệu:\n"
    "   - Chỉ trả lời dựa DUY NHẤT vào Context. Không bịa đặt thông tin.\n"
    "   - Nếu Context không có đáp án, hãy nói rõ là tài liệu không đề cập.\n"
    "   - Bắt buộc đính kèm trích dẫn nguồn ở cuối mỗi ý quan trọng sử dụng thông tin từ tài liệu đó theo đúng định dạng sau:\n"
    "     `- tên_file, Trang X` (ví dụ: `- giao_trinh_triet_hoc.pdf, Trang 12` hoặc `- mac_lenin.pdf, Trang 5`)\n"
    "     Trong đó `tên_file` và `X` lấy chính xác từ trường `source` và `page` được cung cấp trong Context.\n\n"
    "Context:\n{context}"
)


@dataclass
class RetrievedContext:
    document_id: str
    chunk_id: str
    source: str
    page: int
    score: float | None
    snippet: str
    text: str


class ChatRuntimeService:
    def __init__(self) -> None:
        self._embeddings = None

    def _get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = build_embeddings_from_common()
        return self._embeddings

    def _build_context(self, contexts: list[RetrievedContext]) -> str:
        if not contexts:
            return ""
        blocks: list[str] = []
        for idx, item in enumerate(contexts, start=1):
            blocks.append(
                f"[Doc {idx} | source={item.source} | page={item.page} | chunk_id={item.chunk_id}]\n{item.text}"
            )
        return "\n\n---\n\n".join(blocks)

    def _citations_from_context(self, contexts: list[RetrievedContext]) -> list[dict]:
        citations: list[dict] = []
        for item in contexts:
            citation = {
                "source": item.source,
                "page": item.page,
                "snippet": item.snippet,
                "document_id": item.document_id,
                "chunk_id": item.chunk_id,
            }
            if item.score is not None:
                citation["score"] = float(item.score)
            citations.append(citation)
        return citations

    def citations_from_context(self, contexts: list[RetrievedContext]) -> list[dict]:
        return self._citations_from_context(contexts)

    def retrieve(self, db: Session, question: str, *, pipeline_version: str, user_id: str | None = None) -> list[RetrievedContext]:
        if user_id:
            excel_svc = _get_excel_query_service()
            excel_result = excel_svc.query(db, user_id, question)
            if excel_result is not None:
                return [RetrievedContext(
                    document_id="excel_sql",
                    chunk_id="sql_result",
                    source="excel_table",
                    page=0,
                    score=1.0,
                    snippet=excel_result[:280],
                    text=excel_result,
                )]

        mode = settings.retrieval_mode
        if mode == "hybrid":
            return self._retrieve_hybrid(db, question, pipeline_version=pipeline_version)
        return self._retrieve_dense(db, question, pipeline_version=pipeline_version)

    def _retrieve_hybrid(self, db: Session, question: str, *, pipeline_version: str) -> list[RetrievedContext]:
        # Run-ready hybrid stub: keep same interface and return dense results,
        # while reserving hook points for future sparse merge + RRF.
        logger.info("hybrid_mode_stub_dense_passthrough")
        return self._retrieve_dense(db, question, pipeline_version=pipeline_version)

    def _retrieve_dense(self, db: Session, question: str, *, pipeline_version: str) -> list[RetrievedContext]:
        vector = self._get_embeddings().embed_query(question)
        client = build_qdrant_client()
        query_filter = rest.Filter(
            must=[
                rest.FieldCondition(key="pipeline_version", match=rest.MatchValue(value=pipeline_version)),
                rest.FieldCondition(key="kind", match=rest.MatchValue(value="child")),
            ]
        )

        try:
            hits = client.search(
                collection_name=settings.qdrant_collection,
                query_vector=vector,
                query_filter=query_filter,
                limit=settings.retrieval_top_k,
                with_payload=True,
            )
        except Exception as exc:
            logger.warning(f"Qdrant search failed (likely empty/missing collection): {exc}")
            return []

        ranked_parents: dict[str, dict] = {}
        for hit in hits:
            payload = hit.payload or {}
            parent_chunk_id = payload.get("parent_chunk_id")
            if not parent_chunk_id:
                continue
            parent_id = str(parent_chunk_id)
            score = float(hit.score) if hit.score is not None else None
            existing = ranked_parents.get(parent_id)
            if existing is None or (score is not None and (existing.get("score") is None or score > existing["score"])):
                ranked_parents[parent_id] = {
                    "score": score,
                    "document_id": str(payload.get("document_id", "")),
                }

        if not ranked_parents:
            return []

        parent_ids = list(ranked_parents.keys())
        parent_rows = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.id.in_(parent_ids),
                DocumentChunk.kind == "parent",
                DocumentChunk.pipeline_version == pipeline_version,
            )
            .all()
        )
        parent_map = {row.id: row for row in parent_rows}

        ordered: list[RetrievedContext] = []
        for parent_id in sorted(
            ranked_parents,
            key=lambda key: (
                ranked_parents[key].get("score") is not None,
                ranked_parents[key].get("score") or float("-inf"),
            ),
            reverse=True,
        ):
            row = parent_map.get(parent_id)
            if row is None:
                continue
            text = row.text.strip()
            snippet = text[:280]
            score = ranked_parents[parent_id].get("score")
            ordered.append(
                RetrievedContext(
                    document_id=row.document_id,
                    chunk_id=row.id,
                    source=row.source,
                    page=row.page,
                    score=score,
                    snippet=snippet,
                    text=text,
                )
            )
        return ordered

    def _build_llm_chain(self, provider: str):
        if provider in {"configured", "gemini", "opencode"}:
            explicit_provider = provider if provider == "opencode" else None
            llm = build_chat_llm(model=RagConfig.LLM_MODEL, temperature=0.2, provider=explicit_provider)
        elif provider == "local":
            llm = ChatOllama(
                base_url=settings.local_llm_base_url,
                model=settings.local_llm_model,
                temperature=0.2,
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", _SYSTEM_PROMPT),
                ("human", "Question: {question}"),
            ]
        )
        return prompt | llm | StrOutputParser()

    async def _invoke_provider(self, provider: str, question: str, context_text: str) -> str:
        chain = self._build_llm_chain(provider)
        return await chain.ainvoke({"context": context_text, "question": question})

    async def answer(self, question: str, contexts: list[RetrievedContext]) -> tuple[str, str]:

        mode = settings.llm_mode
        context_text = self._build_context(contexts)

        if mode in {"gemini", "opencode"}:
            cloud_provider = infer_llm_provider(RagConfig.LLM_MODEL, None if mode == "gemini" else mode)
            return await self._invoke_provider(mode, question, context_text), cloud_provider
        if mode == "local":
            return await self._invoke_provider("local", question, context_text), "local"

        # auto mode
        cloud_provider = infer_llm_provider(RagConfig.LLM_MODEL)
        try:
            return await self._invoke_provider(cloud_provider, question, context_text), cloud_provider
        except Exception as exc:
            logger.warning("llm_auto_fallback_to_local: %s unavailable: %s", cloud_provider, str(exc))
            return await self._invoke_provider("local", question, context_text), "local"

    async def stream_answer(self, question: str, contexts: list[RetrievedContext]):

        mode = settings.llm_mode
        context_text = self._build_context(contexts)

        if mode in {"gemini", "opencode"}:
            async for token in self._stream_provider(mode, question, context_text):
                yield token
            return

        if mode == "local":
            async for token in self._stream_provider("local", question, context_text):
                yield token
            return

        # auto mode
        emitted = False
        cloud_provider = infer_llm_provider(RagConfig.LLM_MODEL)
        try:
            async for token in self._stream_provider(cloud_provider, question, context_text):
                emitted = True
                yield token
        except Exception as exc:
            if emitted:
                raise
            logger.warning("llm_auto_stream_fallback_to_local: %s unavailable: %s", cloud_provider, str(exc))
            async for token in self._stream_provider("local", question, context_text):
                yield token

    async def _stream_provider(self, provider: str, question: str, context_text: str):
        chain = self._build_llm_chain(provider)
        async for token in chain.astream({"context": context_text, "question": question}):
            yield token


chat_runtime_service = ChatRuntimeService()
