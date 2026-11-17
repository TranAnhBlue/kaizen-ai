from datetime import date, timedelta
import pytest
from app.modules.forecasting.engine import forecast

def series(n=20,offset=0):
    return [{'date':(date(2026,1,1)+timedelta(days=i)).isoformat(),'value':float(offset+10+i*2)} for i in range(n)]

def test_linear_trend_and_holdout():
    result=forecast(series(),3,warning_max=50)
    assert [x['value'] for x in result['forecast']]==[50,52,54]
    assert result['metrics']['mae'] == 0
    assert result['forecast'][-1]['warning']
    assert result['holdout_points'] >= 2

def test_requires_daily_consecutive():
    items=series(); items.pop(5)
    with pytest.raises(ValueError,match='consecutive'): forecast(items)

def test_requires_sufficient_data():
    with pytest.raises(ValueError,match='8'): forecast(series(7))

def test_zero_series_no_divide_by_zero():
    result=forecast([dict(o,value=0) for o in series()])
    assert result['metrics']['wape_percent'] is None

def test_rejects_nonfinite():
    data=series();data[0]['value']=float('nan')
    with pytest.raises(ValueError,match='finite'):forecast(data)
