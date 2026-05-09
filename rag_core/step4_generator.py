"""
step4_generator.py - Module truy xuất (Retriever) và sinh câu trả lời (LLM Chain).

Sử dụng ChatGoogleGenerativeAI (Gemini) kết hợp với retriever
để tạo RAG chain trả lời câu hỏi kèm citations.
"""

from __future__ import annotations

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

from common.logging_utils import configure_logging, get_logger
from config import Config

configure_logging()
logger = get_logger(__name__)

# ── System Prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = (
    "Bạn là chuyên gia AI, trợ lý học tập cho sinh viên "
    "Đại học Công nghệ (UET). Bạn sẽ nhận được các đoạn trích dẫn "
    "từ giáo trình. Hãy trả lời câu hỏi dựa TRỰC TIẾP trên "
    "các đoạn văn được cung cấp dưới đây.\n\n"
    "Quy tắc:\n"
    "1. Chỉ sử dụng thông tin từ tài liệu được cung cấp.\n"
    "2. Nếu thông tin không đủ, hãy chỉ ra phần nào thiếu "
    "thay vì tự ý bổ sung.\n"
    # "3. Luôn đính kèm số trang (VD: [Trang X]) vào cuối "
    # "mỗi ý quan trọng trong câu trả lời.\n\n"
    "Tài liệu tham khảo:\n"
    "{context}"
)


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
    llm = ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        temperature=0.2,
        google_api_key=Config.GEMINI_API_KEY,
    )

    # 2. Tạo prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    # 3. Tạo chain: stuff documents → LLM
    question_answer_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt,
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
