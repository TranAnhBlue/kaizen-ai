from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.security import require_service_token
from app.modules.forecasting.engine import forecast

router = APIRouter(prefix='/internal/forecasting', tags=['internal-forecasting'], dependencies=[Depends(require_service_token)])

class Observation(BaseModel):
    date: str
    value: float

class ForecastRequest(BaseModel):
    observations: list[Observation] = Field(min_length=8,max_length=1000)
    horizon: int = Field(default=7,ge=1,le=30)
    warning_min: float | None = None
    warning_max: float | None = None

@router.post('/predict')
def predict(payload: ForecastRequest):
    try:
        return forecast([o.model_dump() for o in payload.observations],payload.horizon,payload.warning_min,payload.warning_max)
    except (ValueError, OverflowError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
