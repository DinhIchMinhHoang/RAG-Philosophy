"""
step2_chunker.py - Module Chunking Đa tầng (Hierarchical Parent-Child).

Quy trình 3 bước:
  Bước 2.1 → Tạo Parent Chunks (cắt theo Markdown Header, bảo toàn ngữ cảnh).
  Bước 2.2 → Tạo Child Chunks (chia nhỏ Parent, tối ưu tìm kiếm vector).
  Bước 2.3 → Tiền xử lý Tiếng Việt bằng ViTokenizer (CHỈ trên Child Chunks).

Đầu ra: Tuple (parent_chunks, child_chunks) — cả 2 đều là list[Document].
  • parent_chunks: Văn bản tự nhiên, dùng làm ngữ cảnh cho LLM.
  • child_chunks : Văn bản đã tách từ, dùng để nhúng Vector tìm kiếm.
"""

import os
import json
import uuid
import logging
from langchain.text_splitter import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_core.documents import Document
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def hierarchical_chunking(
    markdown_text: str,
    source_name: str,
) -> tuple[list[Document], list[Document]]:
    """
    Chia văn bản Markdown thành cấu trúc Parent–Child Chunks đa tầng.

    Args:
        markdown_text: Chuỗi Markdown đầy đủ (đầu ra từ step1_parser).
        source_name:   Tên nguồn tài liệu (VD: "Triết_Mác_Lenin.pdf").

    Returns:
        Tuple gồm 2 danh sách:
            - parent_chunks : Các khối lớn, giữ nguyên văn bản gốc (cho LLM đọc).
            - child_chunks  : Các khối nhỏ, đã tách từ Tiếng Việt (cho Vector search).
    """

    # ================================================================
    # BƯỚC 2.1 — Tạo Parent Chunks (cắt theo Header Markdown)
    # ================================================================
    # Cấu hình cắt theo heading cấp 1 (#) và cấp 2 (##).
    # Mỗi khối Parent sẽ chứa toàn bộ nội dung dưới một heading.
    headers_to_split_on: list[tuple[str, str]] = [
        ("#", "Header 1"),
        ("##", "Header 2"),
    ]

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,  # Giữ nguyên heading trong nội dung chunk
    )

    # Cắt văn bản Markdown thành các khối theo header
    raw_parent_docs: list[Document] = md_splitter.split_text(markdown_text)

    logger.info(
        f"[Bước 2.1] Đã tạo {len(raw_parent_docs)} Parent Chunks "
        f"từ nguồn '{source_name}'"
    )

    # --- Gán parent_id và metadata bổ sung cho mỗi Parent Chunk ---
    # Mỗi Parent Chunk nhận một UUID duy nhất (parent_id) để liên kết
    # với các Child Chunks con của nó ở bước tiếp theo.
    parent_chunks: list[Document] = []
    for doc in raw_parent_docs:
        parent_id: str = str(uuid.uuid4())

        # Bổ sung metadata: parent_id, source, loại chunk
        doc.metadata["parent_id"] = parent_id
        doc.metadata["source"] = source_name
        doc.metadata["chunk_type"] = "parent"

        parent_chunks.append(doc)

    logger.info(
        f"[Bước 2.1] ✅ Gán parent_id cho {len(parent_chunks)} Parent Chunks"
    )

    # ================================================================
    # BƯỚC 2.2 — Tạo Child Chunks (chia nhỏ từ Parent, tối ưu search)
    # ================================================================
    # Sử dụng RecursiveCharacterTextSplitter để chia mỗi Parent Chunk
    # thành các Child Chunk có kích thước phù hợp cho embedding.
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHILD_CHUNK_SIZE,         # 500 ký tự
        chunk_overlap=Config.CHILD_CHUNK_OVERLAP,    # 100 ký tự chồng lấp
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    # split_documents() tự động kế thừa metadata từ Document gốc.
    # Nghĩa là mỗi Child Chunk sẽ tự động có: parent_id, source,
    # Header 1, Header 2 — từ Parent Chunk tương ứng.
    child_chunks: list[Document] = child_splitter.split_documents(parent_chunks)

    # Đánh dấu loại chunk và gán child_id riêng cho mỗi Child Chunk
    for child in child_chunks:
        child.metadata["chunk_type"] = "child"
        child.metadata["child_id"] = str(uuid.uuid4())

    logger.info(
        f"[Bước 2.2] ✅ Đã tạo {len(child_chunks)} Child Chunks "
        f"từ {len(parent_chunks)} Parent Chunks "
        f"(size={Config.CHILD_CHUNK_SIZE}, overlap={Config.CHILD_CHUNK_OVERLAP})"
    )

    # ================================================================
    # BƯỚC 2.3 — Tiền xử lý Tiếng Việt (Vietnamese Word Segmentation)
    # ================================================================
    # Chỉ áp dụng ViTokenizer lên Child Chunks (dùng cho vector search).
    # KHÔNG chạy trên Parent Chunks để giữ văn bản tự nhiên khi đưa vào LLM.
    #
    # Ví dụ tách từ:
    #   "Triết học Mác Lênin" → "Triết_học Mác_Lênin"
    # Giúp mô hình embedding Tiếng Việt hiểu đúng ranh giới từ ghép.
    from pyvi import ViTokenizer

    for child in child_chunks:
        child.page_content = ViTokenizer.tokenize(child.page_content)

    logger.info(
        f"[Bước 2.3] ✅ Đã tách từ Tiếng Việt (ViTokenizer) "
        f"trên {len(child_chunks)} Child Chunks"
    )

    return parent_chunks, child_chunks


def save_chunks(
    parent_chunks: list[Document],
    child_chunks: list[Document],
    source_name: str,
) -> str:
    """
    Lưu Parent Chunks vào data/stores/doc_store/ dưới dạng JSON.

    Mỗi file JSON chứa danh sách các Parent Chunk với:
      - parent_id: Mã định danh duy nhất.
      - metadata:  Header 1, Header 2, source, chunk_type.
      - content:   Nội dung văn bản tự nhiên (chưa tách từ).
      - child_ids: Danh sách child_id liên kết.

    Args:
        parent_chunks: Danh sách Parent Chunks.
        child_chunks:  Danh sách Child Chunks (để lấy child_id liên kết).
        source_name:   Tên tài liệu nguồn.

    Returns:
        Đường dẫn tới file JSON đã lưu.
    """
    # Tạo thư mục doc_store nếu chưa tồn tại
    os.makedirs(Config.DOC_STORE_DIR, exist_ok=True)

    # Xây dựng dữ liệu JSON cho từng Parent Chunk
    store_data: list[dict] = []
    for parent in parent_chunks:
        pid = parent.metadata["parent_id"]

        # Tìm tất cả child_id thuộc parent này
        linked_child_ids = [
            c.metadata["child_id"]
            for c in child_chunks
            if c.metadata.get("parent_id") == pid
        ]

        store_data.append({
            "parent_id": pid,
            "metadata": {
                k: v for k, v in parent.metadata.items()
                if k != "parent_id"  # Tránh lặp
            },
            "content": parent.page_content,
            "child_ids": linked_child_ids,
        })

    # Tên file JSON = tên tài liệu nguồn đổi đuôi
    json_filename = os.path.splitext(source_name)[0] + "_parents.json"
    output_path = os.path.join(Config.DOC_STORE_DIR, json_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(store_data, f, ensure_ascii=False, indent=2)

    logger.info(
        f"💾 Đã lưu {len(store_data)} Parent Chunks → {output_path}"
    )
    return output_path


# ====================================================================
# KHỐI TEST — Chạy trực tiếp file để kiểm chứng pipeline chunking
# ====================================================================
if __name__ == "__main__":
    from config import Config
    from step1_parser import SmartDocumentParser

    # Đọc PDF từ thư mục data/raw/
    pdf_path = os.path.join(Config.RAW_DIR, "SML (1).pdf")
    source_name = os.path.basename(pdf_path)

    print("=" * 70)
    print("  TEST HIERARCHICAL CHUNKING PIPELINE")
    print("=" * 70)

    # Bước 1: Parse PDF → Markdown
    print("\n📄 Đang parse PDF bằng PyMuPDF4LLM...")
    parser = SmartDocumentParser()
    md_text = parser.parse_doc(pdf_path)
    
    if md_text is None:
        print(f"   ⏭️ Bỏ qua (File đã được xử lý trước đó). Không thực hiện Chunking.")
    else:
        print(f"   → Nhận được {len(md_text):,} ký tự Markdown\n")

        # Bước 2: Chunking đa tầng
        print("✂️  Đang thực hiện Hierarchical Chunking...")
        parents, children = hierarchical_chunking(
            markdown_text=md_text,
            source_name=source_name,
        )

        # --- In thống kê ---
        print(f"\n{'─' * 50}")
        print(f"📊 THỐNG KÊ:")
        print(f"   Parent Chunks : {len(parents)}")
        print(f"   Child Chunks  : {len(children)}")
        print(f"{'─' * 50}")

        # --- In mẫu Parent Chunk ---
        if parents:
            print(f"\n📗 MẪU PARENT CHUNK (chunk #0):")
            print(f"   Metadata : {parents[0].metadata}")
            print(f"   Nội dung (200 ký tự đầu):")
            print(f"   {parents[0].page_content[:200]}")

        # --- In mẫu Child Chunk (đã tách từ Tiếng Việt) ---
        if children:
            print(f"\n📙 MẪU CHILD CHUNK (chunk #0):")
            print(f"   Metadata : {children[0].metadata}")
            print(f"   Nội dung (200 ký tự đầu):")
            print(f"   {children[0].page_content[:200]}")

        # --- Kiểm tra liên kết Parent–Child ---
        if parents and children:
            first_parent_id = parents[0].metadata["parent_id"]
            linked_children = [
                c for c in children
                if c.metadata.get("parent_id") == first_parent_id
            ]
            print(f"\n🔗 KIỂM TRA LIÊN KẾT:")
            print(f"   Parent #0 (id={first_parent_id[:8]}...) "
                  f"có {len(linked_children)} Child Chunks liên kết")

        # --- Lưu Parent Chunks vào data/stores/doc_store/ ---
        print(f"\n💾 Lưu Parent Chunks...")
        saved_path = save_chunks(parents, children, source_name)
        print(f"   Đã lưu: {saved_path}")

    print("\n" + "=" * 70)
    print("  TEST HOÀN TẤT")
    print("=" * 70)
