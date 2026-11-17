# Hướng dẫn Giai đoạn 19

1. Tạo môi trường và khởi động hệ thống theo `README_PHASE18.md`.
2. Tạo hai tenant thử nghiệm với tài khoản khác nhau và ít nhất một Kaizen cho tenant A.
3. Thiết lập biến môi trường `TENANT_A_EMAIL`, `TENANT_A_PASSWORD`, `TENANT_B_EMAIL`, `TENANT_B_PASSWORD`. Không commit mật khẩu.
4. Chạy `python scripts/phase19_acceptance.py --require-complete`.
5. Lưu `artifacts/phase19-acceptance.json`, log Docker, ảnh màn hình và biên bản kiểm thử vào kho bằng chứng nội bộ được kiểm soát quyền.
6. Chạy `python -m unittest discover -s scripts/tests -p test_phase19_acceptance.py -v` để kiểm thử công cụ.

Không sử dụng tài khoản production. Không công bố báo cáo nội bộ chứa thông tin định danh hay URL nội bộ.

## Giới hạn

Không có Docker/PostgreSQL chạy trong môi trường tạo mã nguồn; build thực tế, migration và E2E chưa được xác minh. Chưa có báo cáo đánh giá an toàn thông tin độc lập.
