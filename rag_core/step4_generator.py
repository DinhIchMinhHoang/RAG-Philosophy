"""
step4_generator.py - Module truy xuất (Retriever) và sinh câu trả lời (LLM Chain).

Sử dụng ChatGoogleGenerativeAI (Gemini) kết hợp với retriever
để tạo RAG chain trả lời câu hỏi kèm citations.
"""

from __future__ import annotations

import logging
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.chains.retrieval import create_retrieval_chain

try:
    from .common.llm import build_chat_llm
    from .common.logging_utils import configure_logging, get_logger
    from .common.prompts import SYSTEM_PROMPT
    from .config import Config
except ImportError:  # pragma: no cover
    from common.llm import build_chat_llm
    from common.logging_utils import configure_logging, get_logger
    from common.prompts import SYSTEM_PROMPT
    from config import Config

configure_logging()
logger = get_logger(__name__)


def _format_context_documents(docs) -> str:
    blocks: list[str] = []
    for idx, doc in enumerate(docs or [], start=1):
        metadata = doc.metadata or {}
        source = metadata.get("source", "N/A")
        page = metadata.get("page", "N/A")
        doc_id = metadata.get("doc_id", "")
        chunk_id = metadata.get("chunk_id", "")
        blocks.append(
            (
                f"[C{idx}] source={source} page={page} doc_id={doc_id} chunk_id={chunk_id}\n"
                f"{doc.page_content}"
            )
        )
    return "\n\n---\n\n".join(blocks)


def setup_rag_chain(retriever):
    """
    Thiết lập RAG chain hoàn chỉnh: Retriever → Prompt → LLM.

    Args:
        retriever: Đối tượng retriever từ step3_vector_db.

    Returns:
        RAG chain sẵn sàng nhận câu hỏi qua method invoke().
    """
    logger.info(f"Đang khởi tạo LLM: {Config.LLM_MODEL}")

    # 1. Khởi tạo LLM (Gemini)
    llm = build_chat_llm(temperature=0.2)

    # 2. Tạo prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    # 3. Tạo chain: format retrieved documents with citation IDs → LLM
    question_answer_chain = (
        RunnableLambda(
            lambda inputs: {
                "context": _format_context_documents(inputs.get("context", [])),
                "input": inputs.get("input", ""),
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    # 4. Kết hợp retriever + QA chain → RAG chain
    rag_chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=question_answer_chain,
    )

    logger.info("✅ RAG chain đã sẵn sàng")
    return rag_chain


def ask(rag_chain, question: str) -> dict:
    """
    Gửi câu hỏi tới RAG chain và trả về kết quả.

    Args:
        rag_chain: RAG chain từ setup_rag_chain().
        question: Câu hỏi của người dùng.

    Returns:
        Dict chứa 'answer' (câu trả lời) và 'context' (tài liệu tham khảo).
    """
    logger.info(f"Câu hỏi: \"{question}\"")

    result = rag_chain.invoke({"input": question})

    # Trích xuất thông tin citations từ context
    sources = []
    for doc in result.get("context", []):
        page = doc.metadata.get("page", "N/A")
        source = doc.metadata.get("source", "N/A")
        sources.append({"page": page, "source": source})

    return {
        "answer": result.get("answer", ""),
        "sources": sources,
    }
