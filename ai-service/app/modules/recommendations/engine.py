"""Conservative, explainable rule engine. No fabricated root causes or savings."""
from typing import Any

def generate(kpi: dict[str, Any], run: dict[str, Any]) -> list[dict[str, Any]]:
    points = run.get("values") or []
    if not points:
        return []
    code = str(kpi["code"])
    direction = kpi.get("direction", "HIGHER_BETTER")
    target = kpi.get("target")
    alerts = []
    for p in points:
        value = float(p["value"])
        if target is not None:
            bad = value < float(target) if direction == "HIGHER_BETTER" else value > float(target)
        else:
            bad = bool(p.get("warning"))
        if bad:
            alerts.append({"date": str(p["date"])[:10], "value": value})
    if not alerts:
        return []
    ratio = len(alerts) / len(points)
    priority = "HIGH" if ratio >= 0.5 else "MEDIUM"
    if target is not None:
        basis = f"{len(alerts)}/{len(points)} ngày dự báo không đạt mục tiêu KPI {code}."
    else:
        basis = f"{len(alerts)}/{len(points)} ngày dự báo có cờ cảnh báo KPI {code}."
    return [{
        "title": f"Rà soát xu hướng KPI {code}",
        "rationale": basis,
        "suggested_action": "Kiểm tra dữ liệu đầu vào, xác minh nguyên nhân cùng bộ phận phụ trách, lập thử nghiệm PDCA quy mô nhỏ và theo dõi KPI trước/sau.",
        "priority": priority,
        "evidence": {"forecast_run_id": run["id"], "kpi_code": code, "flagged_dates": alerts, "total_days": len(points), "target": target, "direction": direction, "model": run.get("model")},
        "limitations": "Đề xuất dựa trên quy tắc và dữ liệu dự báo; không chứng minh nguyên nhân gốc, hiệu quả hoặc lợi ích tài chính. Cần chuyên gia phê duyệt."
    }]
