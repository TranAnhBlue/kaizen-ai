import secrets
from fastapi import Header, HTTPException
from app.core.config import settings

def require_service_token(authorization: str = Header(default='')) -> None:
    expected = f'Bearer {settings.ai_service_token}'
    if not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail='Unauthorized')
