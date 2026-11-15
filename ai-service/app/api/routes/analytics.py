from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.core.security import require_service_token
from app.modules.analytics.kpi_analyzer import summarize_kpi
router = APIRouter(prefix='/internal/analytics', tags=['analytics'], dependencies=[Depends(require_service_token)])
class KPIRequest(BaseModel):
    values: list[float] = Field(min_length=1, max_length=10000)
    threshold: float | None = None
@router.post('/summary')
def summary(payload: KPIRequest):
    return summarize_kpi(payload.values, payload.threshold)
