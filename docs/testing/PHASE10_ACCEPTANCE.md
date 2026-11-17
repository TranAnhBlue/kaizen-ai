# Giai đoạn 10 — Checklist nghiệm thu tích hợp

## Điều kiện bắt buộc
- [ ] PostgreSQL/pgvector và Redis hoạt động; migration deploy thành công trên database trống.
- [ ] Backend NestJS và Frontend Next.js build thành công.
- [ ] FastAPI test suite thành công.
- [ ] Chạy `python scripts/phase10_gate.py --live --frontend` với các dịch vụ thật.
- [ ] Tạo tenant A và B; không thể đọc hoặc sửa dữ liệu của tenant khác.
- [ ] Đăng nhập sai và truy cập thiếu quyền bị từ chối.
- [ ] Tạo Kaizen, gửi duyệt, phê duyệt và xác minh audit log.
- [ ] Tạo KPI, nhập dữ liệu, kiểm tra cảnh báo và dữ liệu hiển thị.
- [ ] Chạy dự báo KPI, kiểm tra độ dài, chỉ số sai số và lịch sử.
- [ ] Tạo recommendation, phê duyệt, theo dõi trạng thái.
- [ ] Upload PDF/DOCX; kiểm tra phân quyền tài liệu.
- [ ] Bật embeddings, reindex tài liệu, hỏi chatbot, kiểm tra trích dẫn.
- [ ] Thử prompt injection trong tài liệu; xác minh không lộ dữ liệu.
- [ ] Thử backup/restore trên môi trường staging cô lập.
- [ ] Thu thập logs, bằng chứng test, lỗi tồn đọng, bản ghi build.

**Quy tắc nghiệm thu:** Chưa được đánh dấu hoàn thành khi chưa có bằng chứng chạy thật. Các test tĩnh và unit test không thay thế E2E hoặc đánh giá độc lập.
