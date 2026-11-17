# Kaizen AI – Giai đoạn 19

Kế thừa Giai đoạn 18, bổ sung bộ kiểm thử nghiệm thu API nghiệp vụ **read-only** và báo cáo JSON có PASS/FAIL/SKIP.

- `scripts/phase19_acceptance.py`: xác thực, chặn truy cập ẩn danh, kiểm tra danh sách API, cách ly dữ liệu hai tenant.
- `scripts/tests/test_phase19_acceptance.py`: unit tests mô phỏng API, không yêu cầu mạng.
- `docs/testing/PHASE19_ACCEPTANCE_MATRIX.md`: 10 mục nghiệm thu kỹ thuật.
- `docs/deployment/PHASE19.md`: hướng dẫn vận hành thử và lưu bằng chứng.

**Không tuyên bố đạt Release Candidate:** cần chạy Docker, PostgreSQL, migrations, build và E2E trên môi trường thật.
