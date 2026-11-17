# Giai đoạn 19 – Ma trận nghiệm thu

| Mã | Hạng mục | Minh chứng cần thu thập | Trạng thái mặc định |
|---|---|---|---|
| AT-01 | Đăng nhập, đăng xuất, phiên | API và ảnh giao diện | Chưa kiểm thử |
| AT-02 | Chặn truy cập ẩn danh | JSON phase19 | Chưa kiểm thử |
| AT-03 | Tách biệt tenant A/B | JSON phase19 + bản ghi | Chưa kiểm thử |
| AT-04 | Kaizen tạo và phê duyệt | Biên bản E2E có dữ liệu | Chưa kiểm thử |
| AT-05 | KPI nhập, tổng hợp | Bản ghi KPI và kết quả | Chưa kiểm thử |
| AT-06 | Forecasting | Dữ liệu nguồn, dự báo, sai số | Chưa kiểm thử |
| AT-07 | Recommendations | Bằng chứng, phê duyệt, audit | Chưa kiểm thử |
| AT-08 | RAG tài liệu | Tài liệu, truy vấn, trích dẫn | Chưa kiểm thử |
| AT-09 | Backup/restore | Log phục hồi trên DB thử nghiệm | Chưa kiểm thử |
| AT-10 | Quét ATTT độc lập | Báo cáo của tổ chức độc lập | Chưa thực hiện |

**Quy tắc:** PASS chỉ khi có bằng chứng thực tế. SKIP không được tính là đạt.
Công cụ `phase19_acceptance.py` chỉ chạy kiểm tra HTTP đọc dữ liệu; không thay thế kiểm thử E2E ghi dữ liệu, kiểm tra giao diện hay đánh giá bảo mật độc lập.
