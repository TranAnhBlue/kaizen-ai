# Kaizen AI — Giai đoạn 15

Kế thừa Giai đoạn 14, bổ sung **bộ kiểm thử nghiệm thu API chỉ đọc** có xác thực cookie, kiểm tra API ẩn danh, xác nhận tenant A/B và kiểm tra tenant B không đọc được chi tiết Kaizen của tenant A; workflow CI cho công cụ; ma trận nghiệm thu và hướng dẫn thu thập minh chứng.

- Hướng dẫn: `docs/deployment/PHASE15.md`
- Ma trận nghiệm thu: `docs/testing/PHASE15_ACCEPTANCE_MATRIX.md`
- Kiểm thử đơn vị: `python -m unittest discover -s scripts/tests -p 'test_phase15_e2e.py' -v`
- Kiểm thử dịch vụ thật: `python scripts/phase15_e2e.py --require-complete`

**Chưa chứng nhận Release Candidate / production-ready.** Phải xác nhận build, migration, Docker, luồng nghiệp vụ và đánh giá độc lập trên môi trường thực tế.
