"""
step2_chunker.py - Module chia nhỏ văn bản (Text Splitter).

Sử dụng RecursiveCharacterTextSplitter từ LangChain để chia
danh sách Document thành các chunk nhỏ hơn, giữ nguyên metadata.
"""

import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import Config

logger = logging.getLogger(__name__)


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Chia danh sách Document thành các chunk nhỏ hơn.

    Sử dụng CHUNK_SIZE và CHUNK_OVERLAP từ Config.
    Metadata gốc (source, page, ...) được giữ nguyên cho mỗi chunk.

    Args:
        documents: Danh sách Document gốc (thường mỗi Document = 1 trang PDF).

    Returns:
        Danh sách Document đã được chia nhỏ.
    """
    logger.info(
        f"Bắt đầu chunking: {len(documents)} trang | "
        f"chunk_size={Config.CHUNK_SIZE}, overlap={Config.CHUNK_OVERLAP}"
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)

    logger.info(f"✅ Đã chia thành {len(chunks)} chunks từ {len(documents)} trang")

    return chunks
