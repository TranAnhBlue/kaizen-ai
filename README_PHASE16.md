# Kaizen AI – Giai đoạn 16: Release Candidate verification

Giai đoạn 16 bổ sung release gate **fail-closed**, kiểm tra tệp cấu hình, migration, dịch vụ Compose, kiểm tra secret và HTTP health. Không khẳng định Docker, NestJS/Next.js build hay E2E đã thành công khi chưa chạy thực tế.

## Chạy

```powershell
python -m unittest discover -s scripts/tests -p test_phase16_release.py -v
python scripts/phase16_release.py
# Sau khi cấu hình biến môi trường và khởi động stack Docker:
python scripts/phase16_release.py --secrets --live
```

Báo cáo tại `artifacts/phase16-release.json`. Không lưu giá trị secret. Kết quả FAIL khiến script trả exit code 1.

CI: `.github/workflows/phase16-release.yml` chạy build Next.js/NestJS, Prisma validation, kiểm thử FastAPI và preflight. Kết quả CI chỉ có giá trị sau khi workflow thực sự chạy trên GitHub.

## Chưa hoàn tất

- Chưa có bằng chứng build npm thành công trong môi trường tạo gói (không có cache dependency).
- Chưa có Docker daemon để chạy stack và kiểm thử migration thật.
- Chưa thực hiện E2E nghiệp vụ hoặc đánh giá an toàn thông tin độc lập.
- Phải chạy checklist Giai đoạn 15 và xác minh từng API trước khi tuyên bố RC.
