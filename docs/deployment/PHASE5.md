# Giai đoạn 5: Dự báo KPI bằng mô hình baseline

## Đã triển khai
- `POST /api/v1/forecasting/predict` (JWT; MANAGER/TENANT_ADMIN): chọn KPI, horizon 1–30 ngày.
- `GET /api/v1/forecasting/runs` và `GET /api/v1/forecasting/runs/:id`: dữ liệu cách ly tenant.
- NestJS tổng hợp các phép đo cùng ngày theo trung bình, gửi dữ liệu đã lọc tenant tới FastAPI nội bộ.
- FastAPI `POST /internal/forecasting/predict` (Bearer service token): linear trend, chronological holdout, MAE/RMSE/WAPE, residual anomaly heuristic.
- Lưu lịch sử kết quả vào `forecast_runs`, `forecast_values` và giao diện `/forecasting`.

## Giới hạn
- **Không phải mô hình ML đã huấn luyện theo dữ liệu thực tế của doanh nghiệp.** Đây là baseline thống kê để kiểm tra pipeline.
- Cần 8–1000 ngày liên tiếp; dữ liệu thiếu ngày bị từ chối, không tự điền hoặc suy diễn.
- Chưa tính mùa vụ, ngày nghỉ, yếu tố ngoại sinh hoặc causal inference.
- Cận trên/dưới chỉ là khoảng tham khảo từ RMSE holdout, **không phải** khoảng tin cậy đã hiệu chuẩn.
- Cảnh báo bất thường dựa trên phần dư và MAD; không khẳng định nguyên nhân.
- Các kết quả không tự động chỉnh sửa KPI hay phê duyệt sáng kiến.

## Chạy
1. Tạo `.env` cho backend và AI service theo `.env.example`; `AI_SERVICE_TOKEN` phải trùng nhau.
2. Chạy PostgreSQL, migration: `cd backend && npm install && npx prisma generate && npx prisma migrate deploy && npm run start:dev`.
3. `cd ai-service && pip install -e ".[dev]" && uvicorn app.main:app --reload --port 8000`.
4. `cd frontend && npm install && npm run dev`.
5. Tạo KPI và nhập ít nhất 8 ngày liên tục tại `/kpi`, sau đó vào `/forecasting`.
6. Kiểm thử AI: `cd ai-service && pytest -q`.

## Việc cần làm trước nghiệm thu
- Đối chiếu với dữ liệu KPI thật và các baseline khác (naive, seasonal naive).
- Thiết lập tiêu chí chấp nhận sai số riêng cho từng KPI và đánh giá walk-forward nhiều lần.
- Kiểm soát độ trễ dữ liệu, chất lượng dữ liệu, thay đổi chế độ vận hành và drift.
- Bổ sung worker/queue nếu huấn luyện hoặc dự báo trở thành tác vụ nặng.
- Kiểm thử bảo mật, tenant isolation và đánh giá độc lập trước triển khai thực tế.
