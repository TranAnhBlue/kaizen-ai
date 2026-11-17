from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Any
from app.core.security import require_service_token
from app.modules.recommendations.engine import generate
router = APIRouter(prefix="/internal/recommendations", tags=["recommendations"], dependencies=[Depends(require_service_token)])
class GenerateRequest(BaseModel):
    kpi: dict[str, Any]
    run: dict[str, Any]
@router.post("/generate")
def generate_recommendations(body: GenerateRequest):
    return {"recommendations": generate(body.kpi, body.run)}
