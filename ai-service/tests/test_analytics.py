from app.modules.analytics.kpi_analyzer import summarize_kpi

def test_summary():
    result = summarize_kpi([2.0, 3.0, 4.0], 3.5)
    assert result['average'] == 3.0
    assert result['above_threshold'] is True
