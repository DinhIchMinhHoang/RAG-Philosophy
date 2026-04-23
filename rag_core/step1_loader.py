"""
step1_loader.py - Module đọc dữ liệu PDF.

Sử dụng PyMuPDFLoader từ langchain_community để load file PDF
và trả về danh sách các đối tượng Document (mỗi trang = 1 Document).
"""

import os
import logging
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> list[Document]:
    """
    Đọc file PDF và trả về danh sách Document.

    Args:
        file_path: Đường dẫn tuyệt đối hoặc tương đối tới file PDF.

    Returns:
        Danh sách các đối tượng Document (mỗi trang PDF = 1 Document).

    Raises:
        FileNotFoundError: Nếu file không tồn tại tại đường dẫn đã cho.
    """
    try:
        # Kiểm tra file có tồn tại không
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

        logger.info(f"Đang đọc file PDF: {file_path}")

        # Sử dụng PyMuPDFLoader để load PDF
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()

        logger.info(f"✅ Đã đọc thành công {len(documents)} trang từ '{os.path.basename(file_path)}'")

        return documents

    except FileNotFoundError as e:
        logger.error(f"❌ Lỗi: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi không mong muốn khi đọc PDF: {e}")
        raise

