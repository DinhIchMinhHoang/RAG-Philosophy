# RAG System cho Tài Liệu Học Tập (ML/DL, Toán, Thông Tin Môn Học)

---

## 1. Mục Tiêu Project

Xây dựng một hệ thống **Retrieval-Augmented Generation (RAG)** giúp sinh viên tra cứu, học tập và đặt câu hỏi về:

- Nội dung các môn học: Machine Learning, Deep Learning, Toán (Giải tích, Đại số tuyến tính, Xác suất thống kê)
- Thông tin môn học: đề cương, lịch thi, điểm thành phần, giảng viên
- Tài liệu tham khảo: slide bài giảng, textbook, paper, video transcript

**Kết quả mong đợi:** Chatbot có khả năng trả lời chính xác, có trích dẫn nguồn cụ thể, hoạt động tốt với tài liệu chuyên ngành kỹ thuật (có công thức toán học, ký hiệu đặc thù).

---

## 2. Mô Phỏng Trường Hợp Lý Tưởng

```
Người dùng: "Gradient descent là gì? Nó khác AdaGrad như thế nào?"

[Hệ thống xử lý]
1. Nhận query → embed query thành vector
2. Tìm kiếm top-5 đoạn tài liệu liên quan nhất trong vector store
   → Tìm thấy: slide ML chương 4 trang 12, giáo trình DL chương 6
3. Rerank → lọc lấy 3 đoạn chất lượng nhất
4. Đưa context + query vào LLM prompt
5. LLM sinh câu trả lời có cấu trúc

Chatbot: "Gradient Descent là thuật toán tối ưu hoá dùng đạo hàm...
[giải thích đầy đủ]
...Khác với AdaGrad ở chỗ AdaGrad thích nghi learning rate theo từng tham số...

📎 Nguồn: Slide ML - Tuần 4, trang 12 | Deep Learning (Goodfellow), Chương 6"
```

**Điểm quan trọng trong trường hợp lý tưởng:**
- Câu trả lời không hallucinate — chỉ dùng thông tin trong tài liệu được cung cấp
- Luôn kèm nguồn trích dẫn cụ thể (tên tài liệu, trang/slide)
- Hỗ trợ render công thức LaTeX trong câu trả lời
- Nhận diện khi câu hỏi vượt ngoài phạm vi tài liệu và thông báo cho người dùng

---

## 3. Các Bước Bên Trong RAG

### 3.1 Thu Thập Dữ Liệu (Data Collection)

**Nguồn dữ liệu cần xử lý:**

| Loại tài liệu | Phương pháp thu thập |
|---|---|
| Website trường (đề cương, thông báo) | Web scraping với `BeautifulSoup` + `Scrapy` |
| Slide PDF bài giảng | Upload thủ công hoặc crawl từ LMS |
| Textbook PDF (có text) | `PyMuPDF` (`fitz`) để extract trực tiếp |
| Textbook scan (ảnh) | OCR với `Tesseract` hoặc `Surya OCR` |
| Video bài giảng | Transcript qua `Whisper` (OpenAI) |
| Paper/tài liệu nghiên cứu | `arXiv API` hoặc extract PDF |

**Lưu ý scraping web trường:**
- Cần xử lý đăng nhập vào hệ thống LMS (Moodle, Canvas) — dùng `Selenium` hoặc `Playwright` nếu cần render JavaScript
- Rate limiting: không crawl quá nhanh, thêm delay ngẫu nhiên giữa các request
- Lưu raw HTML + timestamp để có thể re-crawl khi nội dung cập nhật

---

### 3.2 Tiền Xử Lý Dữ Liệu (Preprocessing)

Đây là bước quyết định chất lượng cuối cùng của hệ thống. Tài liệu kỹ thuật có nhiều đặc thù cần xử lý riêng.

**Pipeline tiền xử lý tổng quát:**

```
Raw text → Làm sạch → Chuẩn hóa → Phát hiện cấu trúc → Xử lý đặc thù
```

**Các bước cụ thể:**

1. **Làm sạch cơ bản:** Loại bỏ header/footer lặp lại trong PDF, số trang, watermark, ký tự lỗi encoding (đặc biệt với tiếng Việt UTF-8)

2. **Xử lý công thức toán:** Đây là thách thức lớn nhất cho tài liệu ML/toán
   - Công thức inline LaTeX (`$...$`) và block (`$$...$$`): giữ nguyên hoặc chuyển sang mô tả text
   - Dùng `MathPix API` hoặc `pix2tex` để OCR công thức từ ảnh scan
   - Nếu embed công thức, cân nhắc dùng model embedding hỗ trợ LaTeX

3. **Xử lý bảng biểu:** Dùng `pdfplumber` để extract bảng từ PDF tốt hơn PyMuPDF; với bảng phức tạp dùng `Camelot`

4. **Phát hiện ngôn ngữ:** Tài liệu có thể trộn tiếng Anh và tiếng Việt — dùng `langdetect` để tag metadata

5. **Chuẩn hóa:** Loại bỏ dòng trắng thừa, chuẩn hóa dấu câu, xử lý bullet points không đồng nhất

**Công cụ gợi ý:**

```python
# Extract PDF có text tốt
import fitz  # PyMuPDF
doc = fitz.open("lecture.pdf")
text = "\n".join([page.get_text() for page in doc])

# Extract bảng từ PDF
import pdfplumber
with pdfplumber.open("syllabus.pdf") as pdf:
    tables = pdf.pages[0].extract_tables()

# OCR với Surya (tốt hơn Tesseract cho tài liệu kỹ thuật)
from surya.ocr import run_ocr
```

---

### 3.3 Chunking (Phân Đoạn Tài Liệu)

Chunking ảnh hưởng trực tiếp đến chất lượng retrieval. Không có kích thước chunk "đúng" cho tất cả — cần thử nghiệm.

**Các phương pháp chunking:**

**1. Fixed-size chunking (đơn giản, baseline)**
- Cắt theo số ký tự hoặc token cố định (ví dụ: 512 token)
- Dùng overlap (ví dụ: 50-100 token) để tránh mất context ở ranh giới
- Ưu điểm: đơn giản, dễ kiểm soát. Nhược điểm: thường cắt giữa câu, giữa ý

**2. Recursive character text splitter (khuyến nghị cho tài liệu chung)**
- Thử cắt theo `\n\n`, `\n`, `. `, ` ` theo thứ tự ưu tiên
- Giữ ngữ nghĩa tốt hơn fixed-size
- LangChain cung cấp sẵn: `RecursiveCharacterTextSplitter`

**3. Semantic chunking (chất lượng cao nhất)**
- Tính embedding của từng câu, tìm điểm "ngữ nghĩa thay đổi" để cắt
- Mỗi chunk chứa các câu có nội dung liên quan
- Tốn compute hơn, nhưng cho retrieval accuracy tốt hơn đáng kể
- Thư viện: `LangChain SemanticChunker`, `chonkie`

**4. Document-aware chunking (phù hợp nhất cho tài liệu học thuật)**
- Sử dụng cấu trúc tài liệu: tiêu đề cấp 1, cấp 2, cấp 3 làm ranh giới chunk
- Mỗi chunk = một section/subsection có heading đi kèm
- Cần parser biết cấu trúc: `Unstructured.io`, `LlamaParse`, `Docling`
- **Khuyến nghị cho project này** vì slide và textbook thường có heading rõ ràng

**5. Parent-child chunking (hybrid, rất hiệu quả)**
- Lưu hai cấp: chunk nhỏ (128 token) cho retrieval chính xác + chunk lớn (512 token) là "parent" để cung cấp context đầy đủ cho LLM
- Khi retrieve, lấy chunk nhỏ khớp nhất → trả về parent chunk kèm theo
- LlamaIndex gọi là `HierarchicalNodeParser`

**Thông số khởi điểm cho tài liệu kỹ thuật:**

```
Chunk size: 400-600 token
Overlap: 50-100 token  
Minimum chunk size: 100 token (loại bỏ chunk quá nhỏ)
```

**Metadata cần gắn vào mỗi chunk:**
```json
{
  "source": "slide_ML_week4.pdf",
  "page": 12,
  "chapter": "Gradient Descent",
  "course": "Machine Learning",
  "doc_type": "slide",
  "language": "vi",
  "chunk_index": 3,
  "total_chunks": 45
}
```

---

### 3.4 Embedding

Chuyển đổi các chunk text thành vector số để so sánh ngữ nghĩa.

**Lựa chọn embedding model:**

| Model | Ưu điểm | Nhược điểm | Phù hợp |
|---|---|---|---|
| `text-embedding-3-small` (OpenAI) | Chất lượng cao, nhanh | Tốn phí API | Production |
| `text-embedding-3-large` (OpenAI) | Tốt nhất trên MTEB | Đắt hơn | Khi accuracy quan trọng |
| `bge-m3` (BAAI) | Open-source, đa ngôn ngữ tốt | Cần self-host | **Khuyến nghị** (hỗ trợ tiếng Việt) |
| `multilingual-e5-large` | Đa ngôn ngữ mạnh | Cần self-host | Tài liệu tiếng Việt |
| `nomic-embed-text` | Miễn phí, context dài | Yếu hơn OpenAI | Dev/prototype |

**Lưu ý quan trọng:** `bge-m3` hỗ trợ tốt cả tiếng Anh và tiếng Việt, đây là lựa chọn tốt nhất cho project có tài liệu song ngữ.

---

### 3.5 Vector Store (Lưu Trữ và Index)

**So sánh các vector database:**

| Database | Ưu điểm | Nhược điểm | Phù hợp |
|---|---|---|---|
| **FAISS** | Nhanh, miễn phí, local | Không có UI, không scale distributed | Dev/prototype nhỏ |
| **Qdrant** | Filtering mạnh, self-host, hybrid search | Cần setup | **Khuyến nghị cho production** |
| **ChromaDB** | Dễ dùng, local/cloud | Scale hạn chế | Prototype nhanh |
| **Weaviate** | Hybrid search tích hợp, GraphQL | Phức tạp hơn | Khi cần tính năng nâng cao |
| **Pinecone** | Managed, scale tốt | Tốn phí | Production không muốn tự quản lý infra |

**Ngoài dense vector, cần lưu thêm:**
- BM25 sparse index (cho keyword search) — Elasticsearch hoặc `rank_bm25` library
- Metadata filter index (lọc theo môn học, loại tài liệu)

---

### 3.6 Xử Lý Truy Vấn (Query Processing)

Câu hỏi thô của người dùng thường không tối ưu cho retrieval. Một số kỹ thuật cải thiện:

**1. Query rewriting:** Dùng LLM viết lại câu hỏi rõ ràng hơn, thêm từ khóa kỹ thuật  
Ví dụ: "cái loss function đó là gì?" → "Cross-entropy loss function định nghĩa và công thức"

**2. HyDE (Hypothetical Document Embedding):** Yêu cầu LLM tạo một "đoạn văn giả" có thể trả lời câu hỏi, sau đó embed đoạn văn giả đó để tìm kiếm. Hiệu quả khi câu hỏi ngắn/mơ hồ.

**3. Query expansion:** Thêm từ đồng nghĩa, từ liên quan (ví dụ: "gradient descent" → thêm "SGD", "optimization", "backpropagation")

**4. Multi-query retrieval:** Sinh 3-5 biến thể câu hỏi, retrieve từng cái, merge kết quả

---

### 3.7 Retrieval

**Hybrid search (khuyến nghị):** Kết hợp dense retrieval (semantic) và sparse retrieval (keyword BM25):

```
Score cuối = α × Dense_score + (1-α) × BM25_score
```

Với tài liệu kỹ thuật có thuật ngữ đặc thù (tên hàm, ký hiệu toán), BM25 đóng vai trò quan trọng để tìm đúng thuật ngữ chính xác.

**Reranking:** Sau khi lấy top-20 kết quả từ hybrid search, dùng cross-encoder để rerank lấy top-5 chất lượng nhất:
- Model: `bge-reranker-v2-m3` (BAAI) hoặc `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Reranker chậm hơn nhưng chính xác hơn bi-encoder nhiều

**Cấu hình retrieval:**
```
Top-k retrieval ban đầu: 20
Sau rerank lấy: 5
Context window tối đa cho LLM: 3000-4000 token
```

---

### 3.8 Generation (Sinh Câu Trả Lời)

**Prompt template cơ bản:**
```
Bạn là trợ lý học tập chuyên về {tên môn học}.
Dựa vào các đoạn tài liệu sau đây, hãy trả lời câu hỏi của sinh viên.
Chỉ sử dụng thông tin trong tài liệu được cung cấp. Nếu không tìm thấy thông tin, 
hãy nói rõ là không có trong tài liệu.
Kèm theo số trang/slide nguồn trong câu trả lời.

[TÀI LIỆU]
{retrieved_contexts}

[CÂU HỎI]
{user_question}

[TRẢ LỜI]
```

**Lựa chọn LLM:**

| Model | Ưu điểm | Nhược điểm |
|---|---|---|
| GPT-4o / GPT-4o-mini | Chất lượng cao, tiếng Việt tốt | Tốn phí |
| Claude 3.5 Sonnet | Reasoning tốt, context dài | Tốn phí |
| Gemini 1.5 Flash | Context rất dài (1M token), rẻ | — |
| Llama 3.1 70B (self-host) | Miễn phí, kiểm soát data | Cần GPU mạnh |
| Qwen2.5-7B (self-host) | Nhẹ, tiếng Việt ổn | Chất lượng thấp hơn |

---

## 4. Edge Cases và Vấn Đề Có Thể Phát Sinh

### 4.1 Vấn Đề Về Dữ Liệu

**Công thức toán không được embed tốt:** Câu hỏi "cho tôi xem công thức của softmax" có thể không retrieve đúng nếu công thức được lưu dưới dạng ảnh trong PDF. Giải pháp: dùng MathPix OCR, hoặc thêm mô tả text bên cạnh công thức.

**Tài liệu tiếng Việt có dấu lỗi:** PDF scan từ sách vật lý hoặc tài liệu cũ thường có lỗi encoding. Cần preprocessing chuẩn hóa unicode (NFC normalization).

**Tài liệu trùng lặp:** Cùng một nội dung xuất hiện trong nhiều slide/giáo trình. Cần deduplication dựa trên hash hoặc semantic similarity.

**Slide có nhiều bullet ngắn, ít context:** "Overfitting" một mình trên slide không đủ context để trả lời. Giải pháp: parent-child chunking hoặc gắn nội dung của nhiều slide liên tiếp.

### 4.2 Vấn Đề Về Retrieval

**Câu hỏi quá chung chung:** "Giải thích machine learning" sẽ retrieve hàng chục đoạn, khó chọn cái nào tốt nhất. Cần MMR (Maximal Marginal Relevance) để đa dạng hóa kết quả.

**Câu hỏi cross-chapter:** "So sánh CNN và RNN" — thông tin nằm ở hai chỗ khác nhau trong tài liệu. Retrieval cần lấy từ cả hai nguồn và LLM phải tổng hợp.

**Câu hỏi về thông tin thay đổi theo năm:** "Lịch thi môn X khi nào?" — cần đảm bảo tài liệu được update định kỳ và chunk cũ được thay thế (cần versioning trong metadata).

**False positive retrieval:** Từ "gradient" có thể xuất hiện trong nhiều môn (toán, vật lý, ML). Cần metadata filtering theo môn học trong retrieval.

### 4.3 Vấn Đề Về Generation

**Hallucination:** LLM tự thêm thông tin không có trong context. Giải pháp: tăng temperature thấp, thêm system prompt nhấn mạnh chỉ dùng tài liệu cung cấp, implement citation checking.

**Context quá dài:** 5 chunk × 500 token = 2500 token, cộng với system prompt và câu trả lời có thể vượt context limit. Giải pháp: nén context (summarize) hoặc giảm số chunk.

**Câu hỏi ngoài phạm vi:** Người dùng hỏi về nội dung không có trong tài liệu. Cần implement "out-of-scope detection" — nếu score của tất cả retrieved chunks đều thấp hơn threshold, trả về thông báo không tìm thấy.

### 4.4 Vấn Đề Hệ Thống

**Cold start:** Khi mới deploy, vector store trống. Cần pipeline batch indexing chạy offline trước.

**Tài liệu mới:** Khi giảng viên upload slide mới, cần incremental indexing (chỉ index tài liệu mới, không re-index toàn bộ).

**Latency:** Reranking + LLM generation có thể mất 5-10 giây. Cần streaming response và loading indicator UX tốt.

**Chi phí API:** Với nhiều người dùng, chi phí embedding + LLM có thể tốn. Cân nhắc caching kết quả cho câu hỏi phổ biến.

---

## 5. Framework và Tech Stack

### 5.1 Orchestration Framework

| Framework | Lý do chọn | Thay thế |
|---|---|---|
| **LlamaIndex** ⭐ | Tối ưu cho RAG, nhiều node parser sẵn có, hỗ trợ parent-child chunking, query pipeline linh hoạt | LangChain |
| **LangChain** | Ecosystem rộng, nhiều tài liệu, LCEL pipeline | LlamaIndex |
| **Haystack** | Tốt cho production pipeline, nhiều evaluator tích hợp | LangChain |

**Khuyến nghị:** LlamaIndex cho RAG thuần túy; LangChain nếu cần tích hợp nhiều tool/agent phức tạp hơn.

### 5.2 Document Parsing

| Tool | Mục đích | Thay thế |
|---|---|---|
| **Docling** (IBM) ⭐ | Parse PDF phức tạp, bảng, công thức, đa ngôn ngữ | LlamaParse |
| **LlamaParse** | Parse PDF chất lượng cao (có phí), trả về Markdown | Docling |
| **Unstructured.io** | Parse nhiều định dạng file (PDF, DOCX, HTML...) | Docling |
| **PyMuPDF (fitz)** | Extract text nhanh từ PDF có text layer | pdfplumber |
| **pdfplumber** | Extract bảng từ PDF tốt | Camelot |
| **Surya OCR** | OCR tài liệu scan, tốt hơn Tesseract cho kỹ thuật | Tesseract + Pytesseract |
| **Whisper** (OpenAI) | Transcribe video/audio bài giảng | Faster-Whisper (local) |

### 5.3 Embedding Models

| Model | Lý do chọn | Thay thế |
|---|---|---|
| **bge-m3** (BAAI) ⭐ | Open-source, đa ngôn ngữ (Anh + Việt), hỗ trợ hybrid search dense+sparse | multilingual-e5-large |
| **text-embedding-3-small** (OpenAI) | Chất lượng cao, nhanh, API đơn giản | Cohere embed-v3 |
| **nomic-embed-text** | Miễn phí, context 8192 token | bge-base-en |

### 5.4 Vector Database

| Database | Lý do chọn | Thay thế |
|---|---|---|
| **Qdrant** ⭐ | Self-host được, hybrid search tích hợp, filtering mạnh, UI dashboard | Weaviate |
| **ChromaDB** | Nhanh để prototype, dễ dùng, embed local | FAISS |
| **FAISS** | Cực nhanh, tốt cho scale nhỏ local | — |
| **Pinecone** | Managed, không cần DevOps | Qdrant Cloud |

### 5.5 LLM

| Model | Lý do chọn | Thay thế |
|---|---|---|
| **GPT-4o-mini** ⭐ | Rẻ, nhanh, tiếng Việt tốt | Claude 3 Haiku |
| **GPT-4o** | Tốt nhất cho câu hỏi phức tạp | Claude 3.5 Sonnet |
| **Llama 3.1 8B** (self-host) | Miễn phí, data privacy | Qwen2.5-7B |
| **Gemini 1.5 Flash** | Context dài 1M token, rẻ | — |

### 5.6 Reranking

| Model | Lý do chọn |
|---|---|
| **bge-reranker-v2-m3** ⭐ | Open-source, đa ngôn ngữ, mạnh |
| **Cohere Rerank** | API đơn giản, chất lượng tốt (có phí) |

### 5.7 Evaluation Framework

| Tool | Mục đích |
|---|---|
| **RAGAS** ⭐ | Đánh giá RAG pipeline: faithfulness, answer relevancy, context precision/recall |
| **TruLens** | Tracing và evaluation cho RAG |
| **LangSmith** | Observability, debugging pipeline LangChain |
| **Arize Phoenix** | Open-source observability |

### 5.8 Web Framework và Backend

| Tool | Mục đích | Thay thế |
|---|---|---|
| **FastAPI** ⭐ | API backend, async, nhanh | Flask |
| **Streamlit** | Prototype UI nhanh | Gradio |
| **Next.js** | Production frontend | — |

### 5.9 Infrastructure

| Tool | Mục đích |
|---|---|
| **Docker + Docker Compose** | Container hóa toàn bộ stack |
| **Ollama** | Self-host LLM local dễ dàng |
| **Redis** | Cache kết quả query phổ biến |

---

## 6. Kiến Trúc Đề Xuất (Theo Giai Đoạn)

### Giai đoạn 1 — Prototype nhanh (1-2 tuần)
```
Documents → PyMuPDF → RecursiveTextSplitter → ChromaDB (local)
                                                      ↓
User query → nomic-embed-text → ChromaDB search → GPT-4o-mini → Response
```

### Giai đoạn 2 — Cải thiện chất lượng (2-4 tuần)
```
Documents → Docling → Document-aware chunking → bge-m3 embed → Qdrant (hybrid)
                                                                      ↓
User query → Query rewriting → Hybrid search → bge-reranker → GPT-4o → Response + citations
```

### Giai đoạn 3 — Production
```
Thêm: Incremental indexing pipeline, RAGAS evaluation, Redis cache, 
      monitoring (Arize Phoenix), streaming response, user feedback loop
```

---

## 7. Tóm Tắt Tech Stack Khuyến Nghị

```
Orchestration:    LlamaIndex
Document parser:  Docling + PyMuPDF + Surya OCR
Embedding:        bge-m3 (self-host) hoặc text-embedding-3-small (API)
Vector DB:        Qdrant (hybrid search)
Reranker:         bge-reranker-v2-m3
LLM:              GPT-4o-mini (production) / Llama 3.1 8B (local/private)
Backend:          FastAPI
Evaluation:       RAGAS
Monitoring:       Arize Phoenix
Infrastructure:   Docker Compose + Ollama (nếu self-host LLM)
```

---

*Tài liệu này là living document — cập nhật theo kết quả evaluation thực tế.*
