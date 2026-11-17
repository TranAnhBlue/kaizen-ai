from app.modules.recommendations.engine import generate

def run(values):
    return {"id":"run-1","model":"linear","values":[{"date":f"2026-11-{i+1:02d}","value":v,"warning":False} for i,v in enumerate(values)]}

def test_no_alert():
    assert generate({"code":"OUTPUT","direction":"HIGHER_BETTER","target":90},run([95,96]))==[]

def test_low_performance():
    result=generate({"code":"OUTPUT","direction":"HIGHER_BETTER","target":90},run([80,85,95]))
    assert result[0]["priority"]=="HIGH"
    assert len(result[0]["evidence"]["flagged_dates"])==2

def test_lower_is_better():
    result=generate({"code":"DEFECT","direction":"LOWER_BETTER","target":3},run([2,4,2]))
    assert result[0]["priority"]=="MEDIUM"

def test_missing_data():
    assert generate({"code":"A"},{"id":"x","values":[]})==[]
