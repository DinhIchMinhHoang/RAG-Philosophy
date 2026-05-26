# BẢNG PHÂN CÔNG NHIỆM VỤ
## ĐỀ TÀI: HỆ THỐNG RAG HỖ TRỢ NGHIÊN CỨU HỌC THUẬT, TÀI LIỆU MÔN HỌC

---

### BẢNG TỔNG HỢP VAI TRÒ

| Thành viên | Vai trò chính | Thành phần phụ trách trong Hạ tầng (Docker) |
| :--- | :--- | :--- |
| **Đinh Ích Minh Hoàng** | Frontend & DevOps Lead | `frontend-user`, `frontend-admin`, `nginx-load-balancer`, `ci-cd-pipeline` |
| **Lê Trung Đức** | Backend & User Data Engineer | `backend-api`, `user-relational-db` |
| **Nguyễn Việt Hà** | RAG Architect & Optimization Specialist | `rag-core-service`, `vector-db`, `redis-cache` (Đồng phụ trách `async-worker`) |
| **Bùi Tiến Dũng** | RAG Core & Data Ingestion Engineer | `rag-core-service`, `vector-db`, `object-storage (MinIO)` (Đồng phụ trách `async-worker`) |

---

### CHI TIẾT PHÂN CÔNG CÔNG VIỆC

#### 1. ĐÌNH ÍCH MINH HOÀNG (Frontend & DevOps Lead)
*Phụ trách toàn bộ giao diện tương tác của người dùng/quản trị và hạ tầng triển khai, đảm bảo hệ thống vận hành ổn định trên Internet.*

* **Frontend Người dùng (User Interface):**
    * Xây dựng giao diện Chatbot thông minh, tiếp nhận câu hỏi của người dùng.
    * Hiển thị câu trả lời dạng **Streaming** (chữ chạy thời gian thực) để tối ưu trải nghiệm.
    * Thiết kế khu vực hiển thị nguồn trích dẫn (citations) hoặc các đoạn văn bản liên quan được hệ thống RAG tìm thấy.
* **Frontend Quản trị (Admin Interface):**
    * Xây dựng màn hình quản lý người dùng (Thêm, xóa, phân quyền hệ thống).
    * Thiết kế trang quản lý kho tài liệu tri thức: kéo-thả file upload, nút xóa tài liệu, nút ra lệnh "Tái Index", và bảng theo dõi trạng thái Ingest của file.
* **Docker & DevOps:**
    * Đóng gói Dockerfile cho cả hai tầng Frontend.
    * Viết file `docker-compose.yml` tổng thể kết nối toàn bộ các service nội bộ (`frontend`, `backend`, `db`, `vector-db`, `worker`, `cache`, `nginx`).
    * Cấu hình **Nginx Load Balancer** điều phối request và hỗ trợ hệ thống chịu tải khi có **nhiều người dùng** truy cập đồng thời.
* **CI/CD & Triển khai (Deployment):**
    * Xây dựng luồng tự động hóa CI/CD (GitHub Actions / GitLab CI) để tự động kiểm tra và build image khi có code mới.
    * Cấu hình và triển khai toàn bộ hệ thống lên môi trường đám mây/Internet (VPS/AWS/GCP) kèm IP tĩnh/tên miền công khai.

---

#### 2. LÊ TRUNG ĐỨC (Backend & User Data Engineer)
*Phụ trách xây dựng hệ thống xương sống API, quản lý dữ liệu người dùng, phân quyền và đảm bảo trải nghiệm người dùng (UX) mượt mà từ phía hệ thống.*

* **Phát triển API Backend:**
    * Thiết kế và xây dựng các RESTful API / WebSockets (FastAPI / ExpressJS / Spring Boot) để kết nối Frontend (Hoàng) với các dịch vụ lõi bên dưới.
    * Xây dựng hệ thống xác thực (Authentication) và phân quyền chặt chẽ giữa User thông thường và Admin (RBAC - Role-Based Access Control).
* **Quản trị Cơ sở dữ liệu (Database cho User):**
    * Thiết kế lược đồ (Schema) SQL/NoSQL để lưu trữ thông tin tài khoản người dùng, quyền truy cập.
    * Lưu trữ lịch sử trò chuyện (Chat history) và nhật ký hoạt động hệ thống (System logs).
* **Tối ưu hóa Trải nghiệm người dùng (UX từ Backend):**
    * Tối ưu hóa tốc độ phản hồi của API, xử lý lỗi hệ thống một cách mượt mà để trả về thông báo rõ ràng cho Frontend.
    * Phối hợp với Hoàng thiết lập luồng kết nối API thời gian thực để hiển thị text-streaming mà không bị gián đoạn.

---

#### 3. NGUYỄN VIỆT HÀ & BÙI TIẾN DŨNG (RAG Core & Ingestion Pipeline)
*Hai thành viên đồng phụ trách xây dựng khối xử lý AI cốt lõi, quản lý Vector DB và luồng xử lý file ngầm.*

* **Xử lý Chung RAG Core & Vector Database:**
    * **RAG Lõi:** Tích hợp các thư viện (LangChain / LlamaIndex), chọn mô hình Embedding và thiết lập luồng truy vấn: *Tiếp nhận câu hỏi -> Vector hóa -> Tìm kiếm ngữ cảnh -> Đẩy vào LLM (OpenAI/Ollama) -> Trả kết quả*.
    * **Vector DB:** Triển khai và cấu hình hệ thống cơ sở dữ liệu vector (Qdrant / Milvus / FAISS), thiết lập chỉ mục (indexing) để tìm kiếm độ tương đồng chính xác và nhanh nhất.
* **Xử lý File Upload của người dùng (Ingestion Pipeline):**
    * Kết hợp xây dựng kho lưu trữ file gốc (**Object Storage** như MinIO hoặc S3).
    * Thiết lập hệ thống hàng đợi tác vụ ngầm (Message Queue như RabbitMQ/Celery) để xử lý file bất đồng bộ: Khi Admin upload file -> Đẩy vào hàng đợi -> Worker ngầm tự động thực hiện *Đọc file -> Cắt nhỏ văn bản (Chunking) -> Embedding -> Đẩy vào Vector DB*. Đảm bảo admin không phải chờ đợi API hoạt động xong.

---

#### 4. NGUYỄN VIỆT HÀ (Bổ sung: Quản lý phiên bản & Cache đa lớp)
*Ngoài công việc chung với Dũng ở phần RAG Core, Hà phụ trách thêm mảng quản trị chất lượng mã nguồn và tối ưu hóa hiệu năng chuyên sâu cho hệ thống.*

* **Quản lý phiên bản (Version Control & Governance):**
    * Quản lý chiến lược phân nhánh Git cho nhóm, giải quyết conflict mã nguồn phức tạp.
    * Thực hiện quản lý phiên bản cho các Prompt (Prompt Versioning) hoặc cấu hình Model nhằm đảm bảo tính nhất quán của kết quả RAG qua các lần nâng cấp.
* **Xây dựng luồng Cache đa lớp (Multi-layer Caching):**
    * Cấu hình hệ thống **Redis Cache** để lưu trữ dữ liệu tại nhiều lớp:
        * *Lớp 1 (API Cache):* Cache các kết quả truy vấn admin ít thay đổi để giảm tải cho Database của Đức.
        * *Lớp 2 (RAG/Embedding Cache):* Lưu trữ các câu hỏi phổ biến và các đoạn vector tương ứng. Nếu người dùng hỏi câu trùng lặp, hệ thống sẽ trả kết quả ngay từ Cache thay vì phải tính toán lại Embedding hoặc gọi LLM, giúp tiết kiệm chi phí API và tăng tốc độ phản hồi lên cực hạn.