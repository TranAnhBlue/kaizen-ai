"""Deterministic baseline forecasts; no pretrained model and no claim of causality."""
from datetime import date, timedelta
from math import isfinite, sqrt
from statistics import mean, median

MIN_POINTS = 8
MAX_POINTS = 1000
MAX_HORIZON = 30

def _fit(y):
    n = len(y)
    center = (n - 1) / 2
    x_var = sum((i - center) ** 2 for i in range(n))
    slope = sum((i - center) * (v - mean(y)) for i, v in enumerate(y)) / x_var if x_var else 0.0
    intercept = mean(y) - slope * center
    return intercept, slope

def forecast(observations, horizon=7, warning_min=None, warning_max=None):
    """Daily observations, unique ISO dates, strictly increasing; missing days are rejected.

    Uses a linear trend fit on daily values. Holdout is chronological, never shuffled.
    Model is refit on all data only after holdout evaluation. Intervals are
    descriptive residual bands, not calibrated prediction intervals.
    """
    if not isinstance(horizon, int) or isinstance(horizon, bool) or not 1 <= horizon <= MAX_HORIZON:
        raise ValueError('horizon must be an integer from 1 to 30')
    if not MIN_POINTS <= len(observations) <= MAX_POINTS:
        raise ValueError('Provide between 8 and 1000 daily observations')
    dates = [date.fromisoformat(o['date']) for o in observations]
    values = [float(o['value']) for o in observations]
    if any(not isfinite(v) or abs(v) > 1e12 for v in values):
        raise ValueError('Values must be finite and within +/-1e12')
    if any((b-a).days != 1 for a,b in zip(dates,dates[1:])):
        raise ValueError('Observations must be consecutive daily dates with no duplicates')
    if warning_min is not None and not isfinite(float(warning_min)):
        raise ValueError('warning_min must be finite')
    if warning_max is not None and not isfinite(float(warning_max)):
        raise ValueError('warning_max must be finite')
    if warning_min is not None and warning_max is not None and float(warning_min)>float(warning_max):
        raise ValueError('warning_min must not exceed warning_max')
    holdout = max(2, min(14, len(values)//5))
    train = values[:-holdout]
    a, b = _fit(train)
    predicted_holdout = [a+b*i for i in range(len(train),len(values))]
    actual_holdout = values[-holdout:]
    mae = mean(abs(p-a) for p,a in zip(predicted_holdout,actual_holdout))
    rmse = sqrt(mean((p-a)**2 for p,a in zip(predicted_holdout,actual_holdout)))
    # WAPE omitted when denominator is zero to avoid misleading percentages.
    denom = sum(abs(v) for v in actual_holdout)
    wape = 100*sum(abs(p-a) for p,a in zip(predicted_holdout,actual_holdout))/denom if denom else None
    a, b = _fit(values)
    residuals = [v-(a+b*i) for i,v in enumerate(values)]
    residual_median = median(residuals)
    mad = median(abs(r-residual_median) for r in residuals)
    # 1.4826 scales MAD to standard deviation for normal residuals.
    sigma = 1.4826*mad
    anomalies = [{'date':d.isoformat(),'value':round(v,4),'residual':round(r,4)} for d,v,r in zip(dates,values,residuals) if sigma>0 and abs(r-residual_median)>3*sigma]
    points = []
    for step in range(1,horizon+1):
        estimate = a+b*(len(values)-1+step)
        points.append({'date':(dates[-1]+timedelta(days=step)).isoformat(),
                       'value':round(estimate,4),
                       'lower':round(estimate-1.96*rmse,4),
                       'upper':round(estimate+1.96*rmse,4),
                       'warning':(warning_min is not None and estimate<float(warning_min)) or (warning_max is not None and estimate>float(warning_max))})
    return {'model':'linear_trend_v1','frequency':'daily','training_points':len(values),
            'holdout_points':holdout,'metrics':{'mae':round(mae,4),'rmse':round(rmse,4),'wape_percent':round(wape,2) if wape is not None else None},
            'forecast':points,'anomalies':anomalies,
            'limitations':'Baseline linear trend. Requires consecutive daily observations. Residual bands are heuristic, not calibrated confidence intervals; anomalies do not establish root cause.'}
