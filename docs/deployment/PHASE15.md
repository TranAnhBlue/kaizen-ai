# Phase 15 — Hướng dẫn demo, kiểm thử và thu thập minh chứng

## 1. Chuẩn bị
- Docker Engine / Docker Desktop, Python 3.12+, và máy có đủ RAM.
- Sao chép `.env.phase14.example` thành `.env.phase14`; thay tất cả secret ví dụ, không commit file `.env`.
- Chỉ sử dụng cơ sở dữ liệu demo. Không chạy `seed:demo` trên production.
- Bảo đảm port 3000, 3001, 8000, 5432 chưa bị chiếm.

## 2. Khởi động và kiểm tra
```powershell
Copy-Item .env.phase14.example .env.phase14
# Chỉnh sửa secret trong .env.phase14
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml config -q
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml up --build -d
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml ps
python scripts/phase14_smoke.py
```

Nếu build/migration lỗi, thu thập log `docker compose ... logs migrate backend frontend ai-service` và sửa trước khi ghi nhận kết quả.

## 3. Kiểm tra API và tenant isolation (read-only)
```powershell
$env:TENANT_A_EMAIL='admin-a@example.com'
$env:TENANT_A_PASSWORD='replace-with-demo-password'
$env:TENANT_B_EMAIL='admin-b@example.com'
$env:TENANT_B_PASSWORD='replace-with-demo-password'
python scripts/phase15_e2e.py --require-complete
```

Hai tài khoản phải thuộc hai tenant khác nhau; tenant A phải có ít nhất một Kaizen để kiểm thử truy cập chéo. Script không tạo hoặc xóa dữ liệu. Nếu thiếu tài khoản, bài test sẽ `SKIP` và `--require-complete` trả về mã lỗi. `artifacts/phase15-e2e.json` chứa kết quả HTTP, không ghi password/token.

## 4. Nghiệm thu nghiệp vụ
Thực hiện thủ công AT-07 tới AT-13 theo `docs/testing/PHASE15_ACCEPTANCE_MATRIX.md`. Lưu ảnh, logs, JSON và mã commit. Phân biệt lỗi sản phẩm, lỗi môi trường, và test chưa thực hiện.

## 5. Giới hạn
Trong môi trường tạo gói này chưa có Docker, nên không có bằng chứng các container khởi động, migration thực tế hay E2E thực tế. Các báo cáo bảo mật nội bộ không thay thế báo cáo do tổ chức độc lập thực hiện.
