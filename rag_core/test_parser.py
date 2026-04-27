"""
test_parser.py - Chạy thử SmartDocumentParser (Step 1).

Test 3 kịch bản:
  1. Parse file PDF mới → Docling (hoặc Fallback PyMuPDF).
  2. Parse lại file cũ  → Bỏ qua (Incremental Processing).
  3. Parse file không tồn tại → FileNotFoundError.
"""

import os
from config import Config
from step1_parser import SmartDocumentParser


def main():
    parser = SmartDocumentParser()

    # Chọn 1 file PDF nhỏ để test nhanh
    pdf_path = os.path.join(Config.RAW_DIR, "Deep Learning.pdf")
    source_name = os.path.basename(pdf_path)

    print("=" * 70)
    print("  TEST SmartDocumentParser (Docling → Fallback PyMuPDF)")
    print("=" * 70)

    # ── Test 1: Parse file mới ─────────────────────────────────
    print(f"\n🧪 Test 1: Parse file MỚI — {source_name}")
    md_text = parser.parse_doc(pdf_path)

    if md_text is None:
        print("   ⏭️ Bỏ qua (file đã được xử lý trước đó).")
    else:
        print(f"   ✅ Thành công! {len(md_text):,} ký tự Markdown")
        print(f"   --- 500 ký tự đầu tiên ---")
        print(md_text[:500])
        print("   --- Kết thúc preview ---")

        # Lưu Markdown
        saved_path = parser.save_markdown(md_text, source_name)
        print(f"   💾 Đã lưu: {saved_path}")

    # ── Test 2: Parse lại file cũ (phải bị bỏ qua) ────────────
    print(f"\n🧪 Test 2: Parse lại file CŨ — {source_name}")
    md_text_2 = parser.parse_doc(pdf_path)

    if md_text_2 is None:
        print("   ✅ Đúng! File đã bị bỏ qua (Incremental Processing hoạt động).")
    else:
        print("   ❌ Sai! File lẽ ra phải bị bỏ qua.")

    # ── Test 3: Parse file không tồn tại ───────────────────────
    print(f"\n🧪 Test 3: Parse file KHÔNG TỒN TẠI")
    try:
        parser.parse_doc("khong_ton_tai.pdf")
        print("   ❌ Sai! Lẽ ra phải raise FileNotFoundError.")
    except FileNotFoundError as e:
        print(f"   ✅ Đúng! Nhận được FileNotFoundError: {e}")

    print("\n" + "=" * 70)
    print("  TEST HOÀN TẤT")
    print("=" * 70)


if __name__ == "__main__":
    main()
