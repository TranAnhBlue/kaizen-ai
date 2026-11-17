# Giai đoạn 6: Recommendation Engine

## Chức năng
- Sinh đề xuất có giải thích từ các kết quả dự báo KPI đã lưu; không tự suy đoán nguyên nhân gốc.
- Lưu bằng chứng gồm ID lần dự báo, các ngày vượt mục tiêu/ngưỡng và phiên bản mô hình.
- Quy trình `PROPOSED -> APPROVED / REJECTED`, `APPROVED -> IMPLEMENTED` với audit events.
- Chỉ Manager/Tenant Admin tạo hoặc duyệt; người tạo không được tự duyệt/từ chối.
- Bắt buộc ghi lý do từ chối. `IMPLEMENTED` chỉ xác nhận trạng thái thao tác, không chứng minh hiệu quả.

## Chạy
1. Sao lưu PostgreSQL, chạy `npx prisma generate` và `npx prisma migrate deploy` trong backend.
2. Cấu hình `AI_SERVICE_URL` và cùng `AI_SERVICE_TOKEN` ở backend và ai-service.
3. Chạy FastAPI, NestJS, Next.js theo README; truy cập `/recommendations`.
4. Chạy dự báo KPI trước ở `/forecasting`; chọn lần dự báo để tạo đề xuất.
5. Nếu không có ngày dự báo vượt mục tiêu/ngưỡng, kết quả hợp lệ là danh sách trống.

## Hạn chế
- Engine hiện là rule-based, không phải LLM hay causal inference; không đưa ra cam kết tiết kiệm.
- Chưa có tích hợp đề xuất với KaizenProject, đo lường hiệu quả sau triển khai hoặc hệ thống phê duyệt nhiều cấp.
- Cần chạy build frontend/backend và kiểm thử PostgreSQL thực tế trước khi triển khai.
