"""
step2_chunker.py - Module Chunking Đa Tầng (Manual Parent-Child).

Quy trình:
  Bước 2.1 → Chia từng Page Document thành các Parent Documents (ngữ cảnh lớn).
  Bước 2.2 → Chia tiếp mỗi Parent thành các Child Documents (tối ưu vector search).

Thiết kế khóa (doc_id):
  - Mỗi Parent Document nhận một UUID duy nhất (doc_id).
  - Mỗi Child Document thừa kế đúng doc_id từ Parent của nó.
  - MultiVectorRetriever dùng doc_id làm id_key để lookup Parent từ InMemoryStore.

Đầu ra:
  chunk_documents(pages) → (child_docs, parent_docs)
    • child_docs  : List[Document] — nhúng vào Qdrant (vector search).
    • parent_docs : List[Document] — lưu vào InMemoryStore (full context cho LLM).

Metadata được bảo toàn nghiêm ngặt:
  Parent: {'source': str, 'page': int, 'doc_id': str}
  Child:  {'source': str, 'page': int, 'doc_id': str}
"""

from __future__ import annotations

import logging
import uuid
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_core.common.logging_utils import configure_logging, get_logger
from rag_core.config import Config

configure_logging()
logger = get_logger(__name__)

# ── Splitter instances (khởi tạo 1 lần, tái sử dụng) ─────────────────────────
_PARENT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=Config.PARENT_CHUNK_SIZE,
    chunk_overlap=Config.PARENT_CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)

_CHILD_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=Config.CHILD_CHUNK_SIZE,
    chunk_overlap=Config.CHILD_CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def _make_doc_id() -> str:
    """Sinh UUID v4 dạng chuỗi để dùng làm doc_id."""
    return str(uuid.uuid4())


def _split_page_into_parents(page: Document) -> List[Document]:
    """
    Chia một Page Document thành danh sách Parent Documents.

    Mỗi Parent kế thừa metadata gốc {'source', 'page'} của page,
    đồng thời được gán thêm một 'doc_id' UUID duy nhất.

    Args:
        page: Một Document đại diện cho một trang PDF (từ Step 1).

    Returns:
        Danh sách Parent Documents, mỗi cái có metadata đầy đủ.
    """
    # source và page là metadata cốt lõi, BẮT BUỘC phải có
    source: str = page.metadata.get("source", "unknown")
    page_num: int = page.metadata.get("page", -1)

    raw_parents = _PARENT_SPLITTER.create_documents(
        texts=[page.page_content],
        metadatas=[{"source": source, "page": page_num}],
    )

    parents: List[Document] = []
    for raw in raw_parents:
        doc_id = _make_doc_id()
        # Đảm bảo metadata sạch: chỉ giữ source, page và thêm doc_id
        parents.append(
            Document(
                page_content=raw.page_content,
                metadata={
                    "source": source,
                    "page": page_num,
                    "doc_id": doc_id,
                },
            )
        )

    return parents


def _split_parent_into_children(parent: Document) -> List[Document]:
    """
    Chia một Parent Document thành danh sách Child Documents.

    Mỗi Child kế thừa đúng {'source', 'page', 'doc_id'} từ Parent của nó.
    doc_id là khóa liên kết để MultiVectorRetriever tra cứu Parent.

    Args:
        parent: Một Parent Document đã có doc_id trong metadata.

    Returns:
        Danh sách Child Documents, mỗi cái chia sẻ cùng doc_id với Parent.
    """
    source: str = parent.metadata["source"]
    page_num: int = parent.metadata["page"]
    doc_id: str = parent.metadata["doc_id"]

    raw_children = _CHILD_SPLITTER.create_documents(
        texts=[parent.page_content],
        metadatas=[{"source": source, "page": page_num, "doc_id": doc_id}],
    )

    children: List[Document] = []
    for raw in raw_children:
        children.append(
            Document(
                page_content=raw.page_content,
                metadata={
                    "source": source,
                    "page": page_num,
                    "doc_id": doc_id,
                },
            )
        )

    return children


def chunk_documents(
    pages: List[Document],
) -> Tuple[List[Document], List[Document]]:
    """
    Hàm công khai chính: thực hiện Parent-Child Chunking trên toàn bộ pages.

    Luồng xử lý:
      1. Duyệt qua từng Page Document.
      2. Chia mỗi Page thành các Parent Documents (với doc_id riêng).
      3. Từ mỗi Parent, chia tiếp thành các Child Documents (kế thừa doc_id).

    Metadata BẢO ĐẢM bảo toàn ở cả hai tầng:
      Parent: {'source': str, 'page': int, 'doc_id': str}
      Child:  {'source': str, 'page': int, 'doc_id': str}

    Args:
        pages: Danh sách Document từ Step 1 (mỗi Document = 1 trang PDF).

    Returns:
        Tuple (child_docs, parent_docs):
          - child_docs  : List[Document] — để embed vào Qdrant.
          - parent_docs : List[Document] — để lưu vào InMemoryStore.

    Raises:
        ValueError: Nếu danh sách pages rỗng.
    """
    if not pages:
        raise ValueError(
            "Danh sách pages rỗng. "
            "Đảm bảo Step 1 đã trả về ít nhất một Document."
        )

    all_parents: List[Document] = []
    all_children: List[Document] = []

    for page_idx, page in enumerate(pages):
        parents = _split_page_into_parents(page)
        all_parents.extend(parents)

        for parent in parents:
            children = _split_parent_into_children(parent)
            all_children.extend(children)

    logger.info(
        f"[Step 2] ✅ Chunking hoàn tất: "
        f"{len(pages)} pages → "
        f"{len(all_parents)} parent_docs, "
        f"{len(all_children)} child_docs "
        f"(parent: size={Config.PARENT_CHUNK_SIZE}/overlap={Config.PARENT_CHUNK_OVERLAP}, "
        f"child: size={Config.CHILD_CHUNK_SIZE}/overlap={Config.CHILD_CHUNK_OVERLAP})"
    )

    # Trả về theo thứ tự (child_docs, parent_docs) để match với Step 3
    return all_children, all_parents


# ── Self-test block ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import os

    # Thêm thư mục rag_core vào path để import được step1_parser
    sys.path.insert(0, os.path.dirname(__file__))

    from step1_parser import HybridPDFParser

    pdf_files = [
        f for f in os.listdir(Config.RAW_DIR)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print(f"⚠️  Không tìm thấy PDF nào trong {Config.RAW_DIR}")
        sys.exit(0)

    pdf_path = os.path.join(Config.RAW_DIR, pdf_files[0])
    print(f"📄 Đang parse: {pdf_files[0]}")

    parser = HybridPDFParser()
    pages = parser.parse_pdf(pdf_path)

    if not pages:
        print("⚠️  Parser trả về danh sách rỗng.")
        sys.exit(0)

    print(f"   → {len(pages)} trang đã parse\n")

    child_docs, parent_docs = chunk_documents(pages)

    print(f"\n{'─'*55}")
    print(f"📊 KẾT QUẢ:")
    print(f"   Parent docs : {len(parent_docs)}")
    print(f"   Child docs  : {len(child_docs)}")
    print(f"{'─'*55}")

    if parent_docs:
        p = parent_docs[0]
        print(f"\n📗 PARENT MẪU #0:")
        print(f"   metadata : {p.metadata}")
        print(f"   nội dung : {p.page_content[:200]!r}")

    if child_docs:
        c = child_docs[0]
        print(f"\n📙 CHILD MẪU #0:")
        print(f"   metadata : {c.metadata}")
        print(f"   nội dung : {c.page_content[:200]!r}")

    # Kiểm tra tính nhất quán doc_id
    parent_ids = {p.metadata["doc_id"] for p in parent_docs}
    child_ids  = {c.metadata["doc_id"] for c in child_docs}
    orphan_children = child_ids - parent_ids
    print(f"\n🔗 KIỂM TRA doc_id:")
    print(f"   Unique parent doc_ids : {len(parent_ids)}")
    print(f"   Child doc_ids không có parent : {len(orphan_children)}")
    assert not orphan_children, "❌ Có child mồ côi!"
    print("   ✅ Mọi child đều được liên kết với parent")
