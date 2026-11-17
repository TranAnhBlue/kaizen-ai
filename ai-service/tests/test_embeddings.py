import pytest
from fastapi import HTTPException
from app.modules.chatbot.embedding_service import embed_texts, DIMENSION

@pytest.mark.asyncio
async def test_missing_provider(monkeypatch):
    for key in ('EMBEDDING_BASE_URL', 'EMBEDDING_API_KEY', 'EMBEDDING_MODEL'):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(HTTPException) as exc:
        await embed_texts(['Kaizen'])
    assert exc.value.status_code == 503

def test_embedding_dimension():
    assert DIMENSION == 1536
