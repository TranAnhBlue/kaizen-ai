from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.security import require_service_token
router = APIRouter(prefix='/internal', tags=['ai'], dependencies=[Depends(require_service_token)])
class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    tenant_id: str
@router.post('/chat')
def chat(_: ChatRequest):
    raise HTTPException(status_code=501, detail='RAG/LLM not configured; no generated answers available')
@router.post('/forecast')
def forecast():
    raise HTTPException(status_code=501, detail='Forecast model not trained')
@router.post('/recommendations')
def recommend():
    raise HTTPException(status_code=501, detail='Recommendation engine not configured')
