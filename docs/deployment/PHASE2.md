# Kaizen AI – Giai đoạn 2

## Đã thêm
- RBAC cho thao tác workflow, kiểm tra vai trò tại server.
- Workflow: DRAFT → SUBMITTED → APPROVED → IN_PROGRESS → COMPLETED; SUBMITTED → REJECTED → DRAFT (REOPEN).
- Cấm tự duyệt sáng kiến do chính mình tạo; nhân viên chỉ được submit sáng kiến của mình nếu có createdById.
- Chuyển trạng thái có điều kiện chống cập nhật đồng thời và lưu audit event trong cùng transaction.
- API `GET /kaizen/:id`, `PATCH /kaizen/:id/transition`, UI chi tiết và lịch sử.

## Chạy
1. Giải nén, cấu hình .env theo README giai đoạn 1, khởi chạy PostgreSQL.
2. `cd backend && npm install && npx prisma generate && npx prisma migrate deploy && npm run start:dev`
3. `cd frontend && npm install && npm run dev`
4. Đăng nhập, tạo sáng kiến, mở chi tiết để gửi duyệt và chuyển trạng thái theo vai trò.

## Chưa hoàn thành / lưu ý
- Đây là starter, chưa được xác nhận build hoặc chạy E2E trong môi trường này.
- Chưa có UI quản trị user/role; role hiện được cấp trong dữ liệu user.
- Chưa có chữ ký điện tử, quy trình phê duyệt nhiều cấp, thông báo, hoặc bảo đảm tuân thủ quy định cụ thể.
- JWT chứa role tại thời điểm đăng nhập; thay đổi quyền không có hiệu lực ngay đến khi token hết hạn. Nên tra cứu role từ DB hoặc có token revocation trước khi đưa vào production.
- Cần kiểm thử tích hợp với Postgres thực và kiểm tra bảo mật trước triển khai.
