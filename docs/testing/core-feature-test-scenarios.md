# Kịch bản thử nghiệm tính năng cốt lõi

Tài liệu này mô tả các kịch bản thử nghiệm thủ công hoặc E2E cho hiện trạng hệ thống Lumina RAG. Mục tiêu không chỉ là kiểm tra đúng/sai, mà còn làm nổi bật các điểm mạnh của hệ thống: xác thực an toàn, quản trị tập trung, upload có theo dõi tiến trình, và chat RAG có trích dẫn dựa trên nguồn.

## Phạm vi thử nghiệm

- Môi trường khuyến nghị: chạy stack qua Docker Compose hoặc local backend/frontend tương đương.
- API chính: cùng origin qua `/api/*`.
- Tài khoản thường: email `@gmail.com`.
- Tài khoản admin: email `@lumina.com.vn`.
- File upload hợp lệ: PDF, DOCX, HTML/HTM, Markdown.
- File tabular Excel/CSV hiện đang bị tắt có chủ đích và phải trả lỗi rõ ràng.

## 1. Đăng ký, đăng nhập và khôi phục mật khẩu

### 1.1. Đăng ký tài khoản mới và tự động vào hệ thống

**Mục tiêu:** Chứng minh người dùng mới có thể tự tạo tài khoản và nhận JWT ngay sau khi đăng ký.

**Bước thử nghiệm:**

1. Mở màn hình đăng ký.
2. Nhập username mới, email hợp lệ dạng `@gmail.com`, mật khẩu tối thiểu 6 ký tự.
3. Gửi form đăng ký.
4. Kiểm tra chuyển hướng sang dashboard hoặc trạng thái đã đăng nhập.

**Kết quả kỳ vọng:**

- API `POST /api/signup` trả `201`.
- Response có `access_token` và `token_type: "bearer"`.
- Frontend lưu token và cho phép truy cập dashboard.

**Điểm nổi bật:** Luồng onboarding ngắn, không cần bước đăng nhập lại sau đăng ký, giúp người dùng đi thẳng vào workspace.

### 1.2. Đăng nhập thành công và giữ phiên bằng bearer token

**Mục tiêu:** Xác nhận xác thực tập trung bằng JWT hoạt động trên các API được bảo vệ.

**Bước thử nghiệm:**

1. Mở màn hình đăng nhập.
2. Nhập email và mật khẩu đúng.
3. Sau khi đăng nhập, gọi thử một API cần auth như `GET /api/documents` hoặc `GET /api/auth/me`.
4. Tải lại trang và kiểm tra người dùng vẫn ở trạng thái đã đăng nhập.

**Kết quả kỳ vọng:**

- API `POST /api/login` trả `200`.
- Token được lưu ở frontend.
- Các request sau tự gắn header `Authorization: Bearer <token>`.

**Điểm nổi bật:** Cơ chế token cùng origin phù hợp với kiến trúc Nginx `/api/*`, giảm rủi ro lệch endpoint giữa frontend và backend.

### 1.3. Chặn đăng nhập sai và dữ liệu đăng ký không hợp lệ

**Mục tiêu:** Kiểm tra hệ thống phản hồi rõ khi người dùng nhập sai thông tin.

**Bước thử nghiệm:**

1. Đăng nhập bằng mật khẩu sai.
2. Đăng ký bằng email đã tồn tại.
3. Đăng ký bằng username đã tồn tại.
4. Đăng ký bằng mật khẩu dưới 6 ký tự hoặc email không thuộc domain cho phép.

**Kết quả kỳ vọng:**

- Đăng nhập sai trả `401`.
- Email/username trùng trả `400`.
- Mật khẩu yếu hoặc email sai định dạng bị chặn.
- UI hiển thị lỗi, không lưu token lỗi.

**Điểm nổi bật:** Hệ thống xác thực có kiểm soát đầu vào, tránh tạo tài khoản rác và giữ thông báo lỗi đủ rõ để người dùng tự sửa.

### 1.4. Quên mật khẩu bằng mã xác minh ngắn hạn

**Mục tiêu:** Chứng minh người dùng có thể lấy lại tài khoản mà không lộ việc email có tồn tại hay không.

**Bước thử nghiệm:**

1. Gửi `POST /api/password/forgot` với email hợp lệ đã đăng ký.
2. Lấy mã xác minh được gửi qua email hoặc log mock SMTP trong môi trường dev.
3. Gửi `POST /api/password/verify` với email và mã.
4. Gửi `POST /api/password/reset` với mật khẩu mới.
5. Đăng nhập lại bằng mật khẩu mới.

**Kết quả kỳ vọng:**

- Endpoint forgot luôn trả thông báo chung chung.
- Mã hết hạn sau 15 phút.
- Mã đúng trả `{ "verified": true }`.
- Reset thành công xóa mã đã dùng.
- Mật khẩu cũ không còn đăng nhập được.

**Điểm nổi bật:** Thiết kế tránh user enumeration và dùng mã ngắn hạn, phù hợp với yêu cầu bảo mật tài khoản cơ bản.

## 2. Quản trị hệ thống

### 2.1. Phân quyền admin bằng tài khoản nội bộ

**Mục tiêu:** Xác nhận chỉ tài khoản nội bộ mới truy cập được khu vực quản trị.

**Bước thử nghiệm:**

1. Đăng nhập bằng tài khoản thường `@gmail.com`.
2. Gọi `GET /api/admin/users`.
3. Đăng xuất, đăng nhập bằng tài khoản `@lumina.com.vn`.
4. Gọi lại `GET /api/admin/users`.

**Kết quả kỳ vọng:**

- Tài khoản thường nhận `403 Admin access required`.
- Tài khoản admin nhận danh sách user.

**Điểm nổi bật:** Ranh giới admin được kiểm tra ở backend, không phụ thuộc vào việc ẩn/hiện UI ở frontend.

### 2.2. Quản lý người dùng tập trung

**Mục tiêu:** Kiểm tra admin có thể xem, tạo và xóa user từ một API quản trị.

**Bước thử nghiệm:**

1. Admin gọi `GET /api/admin/users`.
2. Tạo user mới bằng `POST /api/admin/users`.
3. Kiểm tra user mới xuất hiện trong danh sách.
4. Xóa user bằng `DELETE /api/admin/users/{user_id}`.

**Kết quả kỳ vọng:**

- User được tạo có `id`, `username`, `email`.
- User bị xóa không còn trong danh sách.
- Nếu user có nội dung liên quan, hệ thống chạy cleanup nội dung của user đó.

**Điểm nổi bật:** Admin có công cụ vận hành vòng đời tài khoản, không cần can thiệp trực tiếp vào database.

### 2.3. Theo dõi thư viện người dùng, notebook và tài liệu

**Mục tiêu:** Làm nổi bật khả năng quan sát toàn bộ dữ liệu học tập/RAG theo user.

**Bước thử nghiệm:**

1. Tạo ít nhất một user có notebook và một tài liệu đã upload.
2. Admin gọi `GET /api/admin/library`.
3. Kiểm tra cấu trúc trả về theo user, notebook và documents.
4. Kiểm tra mỗi document có `latest_job` nếu đã từng ingest.

**Kết quả kỳ vọng:**

- Response gom dữ liệu theo từng user.
- Notebook có danh sách documents.
- Document hiển thị trạng thái ingest mới nhất, stage và progress.

**Điểm nổi bật:** Admin nhìn được sức khỏe dữ liệu RAG ở mức thư viện, rất hữu ích khi hỗ trợ người dùng hoặc demo hệ thống.

### 2.4. Reindex và xóa dữ liệu ở cấp admin

**Mục tiêu:** Xác nhận admin có thể xử lý lại tài liệu hoặc dọn dữ liệu lỗi một cách có kiểm soát.

**Bước thử nghiệm:**

1. Chọn một document hợp lệ trong `GET /api/admin/documents`.
2. Gọi `POST /api/admin/documents/{document_id}/reindex`.
3. Theo dõi job mới được tạo.
4. Gọi `DELETE /api/admin/documents/{document_id}` hoặc `DELETE /api/admin/notebooks/{notebook_id}` khi cần cleanup.

**Kết quả kỳ vọng:**

- Reindex trả `202` với `job_id`, `status`, `pipeline_version`.
- Excel/CSV cũ bị chặn reindex với lỗi rõ vì tabular ingest đang tắt.
- Delete trả trạng thái `deleted` và danh sách `cleanup_errors` nếu có.

**Điểm nổi bật:** Hệ thống có đường vận hành lại pipeline RAG và cleanup vector/object/chunk metadata mà không phá vỡ contract người dùng thường.

## 3. Upload, ingest và quản lý nguồn

### 3.1. Upload tài liệu hợp lệ và theo dõi tiến trình ingest

**Mục tiêu:** Chứng minh upload không bị chặn bởi quá trình xử lý tài liệu nặng.

**Bước thử nghiệm:**

1. Đăng nhập.
2. Upload một file PDF, DOCX, HTML hoặc Markdown qua UI hoặc `POST /api/documents`.
3. Lấy `job_id` từ response.
4. Poll `GET /api/jobs/{job_id}` đến khi `status` là `succeeded`.

**Kết quả kỳ vọng:**

- Upload trả `202` với `document_id`, `job_id`, `status: "queued"`.
- Job đi qua các stage như parsing, chunking, embedding, indexing vector, persisting metadata.
- UI hiển thị tiến trình thay vì đứng chờ request upload.

**Điểm nổi bật:** Kiến trúc tách upload khỏi worker ingest giúp xử lý PDF/OCR/embedding nặng mà vẫn giữ UX phản hồi nhanh.

### 3.2. Kiểm tra metadata và nguồn sẵn sàng cho citation

**Mục tiêu:** Xác nhận tài liệu sau ingest có đủ metadata phục vụ truy xuất và trích dẫn.

**Bước thử nghiệm:**

1. Upload một tài liệu có nhiều trang hoặc nhiều section rõ ràng.
2. Chờ job `succeeded`.
3. Gọi `GET /api/documents`.
4. Kiểm tra document có thông tin filename, object key, MIME type và latest job.

**Kết quả kỳ vọng:**

- Document xuất hiện trong danh sách nguồn.
- Metadata `source`, `page`, `doc_id` được pipeline bảo toàn ở tầng chunk/vector.
- Chat có thể dùng document này làm nguồn trả lời.

**Điểm nổi bật:** Hệ thống giữ metadata nguồn ngay từ ingest, tạo nền cho câu trả lời có citation đáng tin cậy.

### 3.3. Từ chối định dạng không hỗ trợ và Excel/CSV đang tắt

**Mục tiêu:** Chứng minh hệ thống ưu tiên độ ổn định bằng cách chặn các format chưa bật lại.

**Bước thử nghiệm:**

1. Upload file `.csv`.
2. Upload file `.xlsx` hoặc `.xls`.
3. Upload file không hỗ trợ như `.exe`.
4. Kiểm tra danh sách document sau các lần upload lỗi.

**Kết quả kỳ vọng:**

- Excel/CSV trả `400 Unsupported format`.
- File không hỗ trợ bị từ chối.
- Không tạo document/job rác cho upload bị từ chối.

**Điểm nổi bật:** Thay vì xử lý mơ hồ, hệ thống fail rõ ràng để giữ chất lượng RAG và tránh chat bị ảnh hưởng bởi dữ liệu tabular chưa ổn định.

### 3.4. Xóa tài liệu và cleanup an toàn

**Mục tiêu:** Kiểm tra dữ liệu nguồn có thể được gỡ khỏi retrieval mà vẫn giữ audit job cần thiết.

**Bước thử nghiệm:**

1. Upload một document và bắt đầu ingest.
2. Nếu job đang chạy, xóa document bằng `DELETE /api/documents/{document_id}`.
3. Kiểm tra `GET /api/documents` không còn hiển thị document.
4. Gọi lại `GET /api/jobs/{job_id}` để kiểm tra job lịch sử vẫn được authorize nếu còn tombstone.

**Kết quả kỳ vọng:**

- Metadata/chunks/vectors/object được cleanup theo khả năng.
- Active ingest jobs được đánh dấu hủy hoặc không còn ảnh hưởng tới retrieval.
- Document đã xóa không xuất hiện trong chat source selection.

**Điểm nổi bật:** Delete không chỉ xóa UI, mà còn xử lý cả object storage, database và vector store để tránh citation vào tài liệu đã gỡ.

## 4. Chat RAG, notebook và citation

### 4.1. Chat streaming với tài liệu đã ingest

**Mục tiêu:** Chứng minh trải nghiệm hỏi đáp phản hồi tức thời qua SSE.

**Bước thử nghiệm:**

1. Mở notebook có ít nhất một source đã `Ready`.
2. Nhập câu hỏi bám sát nội dung tài liệu.
3. Quan sát token được stream dần trong UI.
4. Kiểm tra final payload có `answer`, `conversation_id`, `message_id`, `rewritten_query`.

**Kết quả kỳ vọng:**

- API `POST /api/chat/stream` trả `text/event-stream`.
- Token event có `type: "token"`.
- Final event có `type: "final"` và `done: true`.
- UI không phải chờ toàn bộ câu trả lời mới hiển thị.

**Điểm nổi bật:** SSE giúp hệ thống tạo cảm giác phản hồi nhanh trong khi vẫn giữ contract final event cho dữ liệu cấu trúc.

### 4.2. Citation có cấu trúc và mở đúng nguồn

**Mục tiêu:** Xác nhận câu trả lời được neo vào tài liệu thay vì trả lời chung chung.

**Bước thử nghiệm:**

1. Hỏi một câu cần dẫn chứng từ tài liệu.
2. Kiểm tra answer có marker citation như `[C1]`.
3. Kiểm tra `citations` trong final event có `citation_id`, `source`, `page`, `snippet`, `document_id`.
4. Click citation hoặc mở source viewer đến file/trang tương ứng.

**Kết quả kỳ vọng:**

- Chỉ citation thật sự xuất hiện trong answer mới được trả về.
- Source viewer mở đúng file.
- Với PDF, viewer có thể nhảy tới page tương ứng.

**Điểm nổi bật:** Citation không chỉ là text trang trí; backend trả dữ liệu trích dẫn có cấu trúc để kiểm chứng nguồn.

### 4.3. Chọn nguồn trong notebook để giới hạn retrieval

**Mục tiêu:** Chứng minh người dùng kiểm soát được phạm vi tri thức khi notebook có nhiều tài liệu.

**Bước thử nghiệm:**

1. Tạo notebook có ít nhất hai source khác chủ đề.
2. Chọn chỉ một source trong sidebar.
3. Hỏi câu có thể bị lẫn nếu lấy tất cả nguồn.
4. Gửi request với `selected_source_ids` hoặc thao tác checkbox tương ứng trong UI.

**Kết quả kỳ vọng:**

- Retrieval chỉ dùng các source đã chọn.
- Nếu bỏ chọn hoặc gửi danh sách rỗng, backend fallback về toàn bộ source trong notebook.
- Source ID không thuộc user/notebook bị trả `404`.

**Điểm nổi bật:** Đây là ưu điểm quan trọng so với chat RAG một kho chung: người dùng có thể thu hẹp ngữ cảnh để câu trả lời chính xác hơn.

### 4.4. Lưu lịch sử hội thoại và hỏi tiếp theo ngữ cảnh

**Mục tiêu:** Kiểm tra notebook giữ được mạch hội thoại để hỗ trợ follow-up.

**Bước thử nghiệm:**

1. Hỏi một câu đầu tiên trong notebook.
2. Hỏi tiếp một câu phụ thuộc ngữ cảnh, ví dụ "ý này khác gì với luận điểm trước?".
3. Rời notebook, mở lại notebook.
4. Gọi hoặc quan sát `GET /api/notebooks/{notebook_id}/conversations/latest`.

**Kết quả kỳ vọng:**

- Backend tạo hoặc tái sử dụng `conversation_id`.
- Câu hỏi tiếp theo dùng history gần nhất để rewrite/retrieval.
- Khi mở lại notebook, conversation mới nhất được load theo notebook và owner.

**Điểm nổi bật:** Chat không chỉ là từng request độc lập; hệ thống có nền tảng conversation theo notebook, giúp trải nghiệm giống workspace học tập hơn.

## Tiêu chí đánh giá chung

- Không có request nào gọi endpoint legacy ngoài `/api/*`.
- Các API bảo vệ đều yêu cầu bearer token.
- UI không hiển thị source/chat/admin data của user khác.
- Upload nặng không làm treo luồng chính của người dùng.
- Chat trả lời dựa trên nguồn, có citation kiểm chứng được.
- Lỗi format, lỗi auth, lỗi admin permission và lỗi empty notebook đều hiển thị rõ ràng.

## Gợi ý dữ liệu demo

- Một PDF triết học 2-5 trang có luận điểm rõ ràng để test citation.
- Một DOCX hoặc Markdown ngắn để chứng minh ingest đa định dạng.
- Một CSV/XLSX nhỏ để chứng minh tabular ingest đang được chặn an toàn.
- Hai notebook khác chủ đề để test source selection và isolation.
- Một tài khoản thường `demo.user@gmail.com` và một tài khoản admin `admin@lumina.com.vn`.
