# Giai đoạn 4 – Chatbot Kaizen theo tài liệu

## Đã có
- API tải TXT/PDF/DOCX (5 MB), FastAPI trích xuất văn bản và chia đoạn.
- Các đoạn được lưu PostgreSQL với tenantId; câu hỏi tìm theo từ khóa trong phạm vi tenant.
- Chat qua NestJS, lưu hội thoại, trả nguồn tham khảo và chế độ truy xuất.
- FastAPI có adapter cho dịch vụ LLM tương thích OpenAI Chat Completions, không cần dùng nếu chỉ muốn thử retrieval.
- Người dùng chỉ xem hội thoại của mình; tải tài liệu cần MANAGER hoặc TENANT_ADMIN.

## Chưa có / hạn chế
- Đây là **retrieval theo từ khóa**, chưa có embeddings, vector similarity hay hybrid search hoàn chỉnh. Cột pgvector của bản trước được giữ làm nền cho bước kế tiếp.
- Chưa có OCR cho PDF scan, chưa có phân quyền theo từng tài liệu, chưa có luồng xóa tài liệu, chưa có kiểm soát quota theo tenant.
- Trích dẫn là danh sách đoạn truy xuất; chưa có kiểm chứng tự động rằng mọi mệnh đề trong câu trả lời được nguồn chứng minh.
- Nếu cấu hình LLM bên thứ ba, đoạn tài liệu sẽ được gửi tới nhà cung cấp đó; cần thẩm định bảo mật, bảo vệ dữ liệu và hợp đồng trước khi dùng dữ liệu thật.
- Dữ liệu file gốc không lưu; chỉ lưu các đoạn text. Cần Object Storage và cơ chế retention ở phiên bản sản xuất.

## Chạy
1. Khởi động PostgreSQL và Redis như Phase 3.
2. `cd backend; npm install; npx prisma generate; npx prisma migrate deploy; npm run start:dev`.
3. `cd ai-service; pip install -e ".[dev]"; uvicorn app.main:app --port 8000`.
4. `cd frontend; npm install; npm run dev`.
5. Đặt **cùng** AI_SERVICE_TOKEN trong backend/.env và ai-service/.env.
6. Truy cập http://localhost:3000/ai-chat.

Để có câu trả lời sinh bởi mô hình, cấu hình LLM_BASE_URL, LLM_API_KEY, LLM_MODEL trong ai-service/.env. Nếu không, API trả đoạn tài liệu liên quan và gắn nhãn `retrieval_only`, không giả lập AI.

## API
- GET /api/v1/ai-chat/documents
- POST /api/v1/ai-chat/documents
- GET /api/v1/ai-chat/conversations
- GET /api/v1/ai-chat/conversations/:id
- POST /api/v1/ai-chat/ask

## Kiểm thử cần làm trước nghiệm thu
- Xác thực/role/tenant isolation; PDF/DOCX hỏng, file quá lớn, PDF scan; câu hỏi không có tài liệu; prompt injection; timeout LLM; tải đồng thời; xóa và lưu trữ dữ liệu; bảo mật nhà cung cấp AI.
