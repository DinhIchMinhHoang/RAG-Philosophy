from __future__ import annotations

import logging
import re
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
    from rag_core.common.embeddings import get_embeddings as get_embeddings_from_common
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
    "Bạn là trợ lý AI học tập thân thiện. Bạn phải luôn trả lời bằng tiếng Việt.\n\n"
    "Quy tắc trả lời:\n"
    "1. Nếu phần Context bên dưới trống:\n"
    "   - Nếu người dùng chào hỏi, hãy chào lại tự nhiên và mời họ tải tài liệu lên.\n"
    "   - Nếu người dùng hỏi kiến thức, hãy từ chối lịch sự vì chưa có tài liệu để tra cứu.\n"
    "2. Nếu phần Context có dữ liệu:\n"
    "   - Chỉ trả lời dựa trên Context. Không bịa đặt thông tin.\n"
    "   - Mọi nhận định dựa trên tài liệu phải kèm marker citation inline như [C1] hoặc [C2].\n"
    "   - Chỉ dùng các marker xuất hiện ở đầu block Context. Không tạo marker mới.\n"
    "   - Nếu Context không có đáp án, hãy nói rõ là tài liệu không đề cập và không gắn citation giả.\n\n"
    "Context:\n{context}"
)

_CITATION_MARKER_RE = re.compile(r"\[(C\d+)\]", re.IGNORECASE)
_CITATION_GROUP_RE = re.compile(r"\[((?:\s*C\d+\s*(?:,\s*)?)+)\]", re.IGNORECASE)


@dataclass
class RetrievedContext:
    document_id: str
    chunk_id: str
    doc_id: str
    source: str
    page: int
    score: float | None
    snippet: str
    text: str


def _clean_context_value(value: str | None) -> str:
    if not value:
        return ""
    return str(value).replace("\n", " ").replace("\r", " ").strip()


class ChatRuntimeService:
    def __init__(self) -> None:
        self._embeddings = None

    def _get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = get_embeddings_from_common()
        return self._embeddings

    def _dedupe_contexts(self, contexts: list[RetrievedContext]) -> list[RetrievedContext]:
        deduped: list[RetrievedContext] = []
        seen: set[tuple[str, str, str, int]] = set()
        for item in contexts:
            key = (item.document_id, item.chunk_id, item.source, item.page)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped

    def _build_context(self, contexts: list[RetrievedContext]) -> str:
        deduped_contexts = self._dedupe_contexts(contexts)
        if not deduped_contexts:
            return ""
        blocks: list[str] = []
        for idx, item in enumerate(deduped_contexts, start=1):
            citation_id = f"C{idx}"
            blocks.append(
                (
                    f"[{citation_id}] source={_clean_context_value(item.source)} "
                    f"page={item.page} doc_id={_clean_context_value(item.doc_id)} "
                    f"chunk_id={_clean_context_value(item.chunk_id)}\n{item.text}"
                )
            )
        return "\n\n---\n\n".join(blocks)

    def _build_history(self, recent_history: list[dict[str, str]] | None) -> str:
        if not recent_history:
            return "No recent chat history."
        lines: list[str] = []
        for item in recent_history:
            role = item.get("role", "").strip() or "unknown"
            content = item.get("content", "").strip()
            if content:
                lines.append(f"{role}: {content}")
        return "\n".join(lines) if lines else "No recent chat history."

    def _citations_from_context(self, contexts: list[RetrievedContext]) -> list[dict]:
        citations: list[dict] = []
        for idx, item in enumerate(self._dedupe_contexts(contexts), start=1):
            citation = {
                "citation_id": f"C{idx}",
                "rank": idx,
                "source": item.source,
                "page": item.page,
                "snippet": item.snippet,
                "document_id": item.document_id,
                "chunk_id": item.chunk_id,
                "doc_id": item.doc_id,
            }
            if item.score is not None:
                citation["score"] = float(item.score)
            citations.append(citation)
        return citations

    def citations_from_context(self, contexts: list[RetrievedContext]) -> list[dict]:
        return self._citations_from_context(contexts)

    def normalize_citation_markers(self, answer: str, citations: list[dict] | None = None) -> str:
        valid_ids = {
            str(item.get("citation_id", "")).upper()
            for item in (citations or [])
            if item.get("citation_id")
        }

        def replace_group(match: re.Match[str]) -> str:
            ids = [item.upper() for item in re.findall(r"C\d+", match.group(1), flags=re.IGNORECASE)]
            if not ids:
                return match.group(0)
            for citation_id in ids:
                if not valid_ids or citation_id in valid_ids:
                    return f"[{citation_id}]"
            return f"[{ids[0]}]"

        return _CITATION_GROUP_RE.sub(replace_group, answer or "")

    def cited_ids_from_answer(self, answer: str) -> list[str]:
        cited_ids: list[str] = []
        seen: set[str] = set()
        normalized_answer = self.normalize_citation_markers(answer)
        for match in _CITATION_MARKER_RE.finditer(normalized_answer):
            citation_id = match.group(1).upper()
            if citation_id in seen:
                continue
            seen.add(citation_id)
            cited_ids.append(citation_id)
        return cited_ids

    def filter_citations_for_answer(self, answer: str, citations: list[dict]) -> list[dict]:
        normalized_answer = self.normalize_citation_markers(answer, citations)
        cited_ids = set(self.cited_ids_from_answer(normalized_answer))
        if not cited_ids:
            if citations:
                logger.warning("answer_missing_citation_markers")
            return []

        citation_map = {str(item.get("citation_id", "")).upper(): item for item in citations}
        filtered = [item for item in citations if str(item.get("citation_id", "")).upper() in cited_ids]
        unknown_ids = sorted(cited_ids.difference(citation_map))
        if unknown_ids:
            logger.warning("answer_unknown_citation_markers: %s", ",".join(unknown_ids))
        return filtered

    def retrieve(
        self,
        db: Session,
        question: str,
        *,
        pipeline_version: str,
        user_id: int | None = None,
        notebook_id: int | None = None,
    ) -> list[RetrievedContext]:
        mode = settings.retrieval_mode
        if mode == "hybrid":
            return self._retrieve_hybrid(
                db,
                question,
                pipeline_version=pipeline_version,
                user_id=user_id,
                notebook_id=notebook_id,
            )
        return self._retrieve_dense(
            db,
            question,
            pipeline_version=pipeline_version,
            user_id=user_id,
            notebook_id=notebook_id,
        )

    def _retrieve_hybrid(
        self,
        db: Session,
        question: str,
        *,
        pipeline_version: str,
        user_id: int | None = None,
        notebook_id: int | None = None,
    ) -> list[RetrievedContext]:
        # Run-ready hybrid stub: keep same interface and return dense results,
        # while reserving hook points for future sparse merge + RRF.
        logger.info("hybrid_mode_stub_dense_passthrough")
        return self._retrieve_dense(
            db,
            question,
            pipeline_version=pipeline_version,
            user_id=user_id,
            notebook_id=notebook_id,
        )

    def _retrieve_dense(
        self,
        db: Session,
        question: str,
        *,
        pipeline_version: str,
        user_id: int | None = None,
        notebook_id: int | None = None,
    ) -> list[RetrievedContext]:
        vector = self._get_embeddings().embed_query(question)
        must_filters = [
            rest.FieldCondition(key="pipeline_version", match=rest.MatchValue(value=pipeline_version)),
            rest.FieldCondition(key="kind", match=rest.MatchValue(value="child")),
        ]
        if user_id is not None:
            must_filters.append(rest.FieldCondition(key="owner_id", match=rest.MatchValue(value=user_id)))
        if notebook_id is not None:
            must_filters.append(rest.FieldCondition(key="notebook_id", match=rest.MatchValue(value=notebook_id)))
        client = build_qdrant_client()
        query_filter = rest.Filter(must=must_filters)

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
        parent_query = db.query(DocumentChunk).filter(
            DocumentChunk.id.in_(parent_ids),
            DocumentChunk.kind == "parent",
            DocumentChunk.pipeline_version == pipeline_version,
        )
        if user_id is not None:
            parent_query = parent_query.filter(DocumentChunk.owner_id == user_id)
        if notebook_id is not None:
            parent_query = parent_query.filter(DocumentChunk.notebook_id == notebook_id)

        parent_rows = parent_query.all()
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
            source = row.document.filename if row.document is not None else row.source
            ordered.append(
                RetrievedContext(
                    document_id=row.document_id,
                    chunk_id=row.id,
                    doc_id=row.doc_id,
                    source=source,
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
                ("human", "Recent chat history:\n{chat_history}"),
                ("human", "Question: {question}"),
            ]
        )
        return prompt | llm | StrOutputParser()

    def _build_rewrite_chain(self, provider: str):
        if provider in {"configured", "gemini", "opencode"}:
            explicit_provider = provider if provider == "opencode" else None
            llm = build_chat_llm(model=RagConfig.LLM_MODEL, temperature=0.0, provider=explicit_provider)
        elif provider == "local":
            llm = ChatOllama(
                base_url=settings.local_llm_base_url,
                model=settings.local_llm_model,
                temperature=0.0,
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Rewrite the latest user question into a standalone retrieval query. "
                    "Use recent chat history only to resolve references like it, that, this, he, she, or the above. "
                    "Do not answer the question. Return only the rewritten query.",
                ),
                ("human", "Recent chat history:\n{chat_history}\n\nLatest user question: {question}"),
            ]
        )
        return prompt | llm | StrOutputParser()

    async def _invoke_provider(self, provider: str, question: str, context_text: str, chat_history_text: str) -> str:
        chain = self._build_llm_chain(provider)
        return await chain.ainvoke({"context": context_text, "question": question, "chat_history": chat_history_text})

    async def _invoke_rewrite_provider(self, provider: str, question: str, chat_history_text: str) -> str:
        chain = self._build_rewrite_chain(provider)
        return await chain.ainvoke({"question": question, "chat_history": chat_history_text})

    async def rewrite_question(self, question: str, recent_history: list[dict[str, str]] | None = None) -> str:
        if not recent_history:
            return question

        mode = settings.llm_mode
        chat_history_text = self._build_history(recent_history)

        try:
            if mode in {"gemini", "opencode"}:
                rewritten = await self._invoke_rewrite_provider(mode, question, chat_history_text)
            elif mode == "local":
                rewritten = await self._invoke_rewrite_provider("local", question, chat_history_text)
            else:
                cloud_provider = infer_llm_provider(RagConfig.LLM_MODEL)
                try:
                    rewritten = await self._invoke_rewrite_provider(cloud_provider, question, chat_history_text)
                except Exception as exc:
                    logger.warning("llm_auto_rewrite_fallback_to_local: %s unavailable: %s", cloud_provider, str(exc))
                    rewritten = await self._invoke_rewrite_provider("local", question, chat_history_text)
        except Exception as exc:
            logger.warning("question_rewrite_failed: %s", str(exc))
            return question

        normalized = rewritten.strip().strip('"').strip("'").strip()
        return normalized or question

    def _append_excel_context(self, db: Session | None, user_id: str | None, question: str, context_text: str) -> str:
        if db is None or not user_id:
            return context_text
        try:
            excel_service = _get_excel_query_service()
            result = excel_service.query(db, user_id, question)
            if result:
                logger.info("excel_query_result: %d chars — %s", len(result), result[:120])
                block = (
                    "[Excel Query Result — không có citation marker, "
                    "không cần gắn [C1] cho dữ liệu này]\n"
                    f"{result}"
                )
                return f"{block}\n\n---\n\n{context_text}" if context_text else block
        except Exception as exc:
            logger.warning("excel_query_failed: %s", str(exc))
        return context_text

    async def answer(
        self,
        question: str,
        contexts: list[RetrievedContext],
        recent_history: list[dict[str, str]] | None = None,
        db: Session | None = None,
        user_id: str | None = None,
    ) -> tuple[str, str]:

        mode = settings.llm_mode
        context_text = self._build_context(contexts)
        context_text = self._append_excel_context(db, user_id, question, context_text)
        chat_history_text = self._build_history(recent_history)

        if mode in {"gemini", "opencode"}:
            cloud_provider = infer_llm_provider(RagConfig.LLM_MODEL, None if mode == "gemini" else mode)
            return await self._invoke_provider(mode, question, context_text, chat_history_text), cloud_provider
        if mode == "local":
            return await self._invoke_provider("local", question, context_text, chat_history_text), "local"

        # auto mode
        cloud_provider = infer_llm_provider(RagConfig.LLM_MODEL)
        try:
            return await self._invoke_provider(cloud_provider, question, context_text, chat_history_text), cloud_provider
        except Exception as exc:
            logger.warning("llm_auto_fallback_to_local: %s unavailable: %s", cloud_provider, str(exc))
            return await self._invoke_provider("local", question, context_text, chat_history_text), "local"

    async def stream_answer(
        self,
        question: str,
        contexts: list[RetrievedContext],
        recent_history: list[dict[str, str]] | None = None,
        db: Session | None = None,
        user_id: str | None = None,
    ):

        mode = settings.llm_mode
        context_text = self._build_context(contexts)
        context_text = self._append_excel_context(db, user_id, question, context_text)
        chat_history_text = self._build_history(recent_history)

        if mode in {"gemini", "opencode"}:
            async for token in self._stream_provider(mode, question, context_text, chat_history_text):
                yield token
            return

        if mode == "local":
            async for token in self._stream_provider("local", question, context_text, chat_history_text):
                yield token
            return

        # auto mode
        emitted = False
        cloud_provider = infer_llm_provider(RagConfig.LLM_MODEL)
        try:
            async for token in self._stream_provider(cloud_provider, question, context_text, chat_history_text):
                emitted = True
                yield token
        except Exception as exc:
            if emitted:
                raise
            logger.warning("llm_auto_stream_fallback_to_local: %s unavailable: %s", cloud_provider, str(exc))
            async for token in self._stream_provider("local", question, context_text, chat_history_text):
                yield token

    async def _stream_provider(self, provider: str, question: str, context_text: str, chat_history_text: str):
        chain = self._build_llm_chain(provider)
        async for token in chain.astream({"context": context_text, "question": question, "chat_history": chat_history_text}):
            yield token


chat_runtime_service = ChatRuntimeService()
