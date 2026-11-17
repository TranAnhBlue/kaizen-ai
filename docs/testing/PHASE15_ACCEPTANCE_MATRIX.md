# Phase 15 — Ma trận kiểm thử nghiệm thu (chưa xác nhận đạt)

| ID | Kịch bản | Minh chứng bắt buộc | Kết quả |
|---|---|---|---|
| AT-01 | Docker Compose khởi động tất cả dịch vụ | `docker compose ps`, logs | NOT RUN |
| AT-02 | Prisma migration áp dụng thành công | `prisma migrate status`, logs | NOT RUN |
| AT-03 | Frontend, Backend, AI Service health | `phase14-smoke.json` | NOT RUN |
| AT-04 | Không đăng nhập không truy cập API bảo vệ | `phase15-e2e.json` | NOT RUN |
| AT-05 | Đăng nhập và kiểm tra tenant A/B | `phase15-e2e.json` | NOT RUN |
| AT-06 | Tenant B không đọc được Kaizen của A | `phase15-e2e.json` | NOT RUN |
| AT-07 | Kaizen workflow với các vai trò | request/response đã ẩn thông tin nhạy cảm | NOT RUN |
| AT-08 | KPI definitions, nhập liệu, analytics | request/response và screenshot | NOT RUN |
| AT-09 | Forecast và recommendation có evidence | JSON đã ẩn danh | NOT RUN |
| AT-10 | Upload tài liệu, RAG, citations | screenshot và JSON | NOT RUN |
| AT-11 | Backup/restore PostgreSQL | checksum, log và đối soát | NOT RUN |
| AT-12 | Quét SAST, dependency, secrets | báo cáo công cụ, issue khắc phục | NOT RUN |
| AT-13 | Đánh giá bảo mật của đơn vị độc lập | báo cáo do tổ chức độc lập phát hành | NOT RUN |

`NOT RUN` không đồng nghĩa `PASS`. Kết quả phải được cập nhật từ thử nghiệm trên môi trường thật; không tự điền thành công. Các bài test đơn vị của runner chỉ kiểm tra logic công cụ, không thay thế kiểm thử hệ thống.
