from statistics import mean

def summarize_kpi(values: list[float], threshold: float | None = None) -> dict:
    if not values:
        raise ValueError('At least one value required')
    return {'count': len(values), 'average': round(mean(values), 4), 'min': min(values), 'max': max(values), 'last': values[-1], 'above_threshold': threshold is not None and values[-1] > threshold}
