"""OpenAI-compatible embeddings; no silent fake-vector fallback."""
import os
import httpx
from fastapi import HTTPException

DIMENSION = 1536

async def embed_texts(texts: list[str]) -> list[list[float]]:
    base = os.getenv('EMBEDDING_BASE_URL', '').rstrip('/')
    key = os.getenv('EMBEDDING_API_KEY', '')
    model = os.getenv('EMBEDDING_MODEL', '')
    if not (base and key and model):
        raise HTTPException(status_code=503, detail='Embedding provider not configured')
    if not texts or len(texts) > 32 or any(len(t) > 8000 for t in texts):
        raise HTTPException(status_code=422, detail='Invalid embedding batch')
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(base + '/embeddings', headers={'Authorization': f'Bearer {key}'}, json={'model': model, 'input': texts})
            response.raise_for_status()
            data = response.json()['data']
        ordered = sorted(data, key=lambda x: x['index'])
        vectors = [row['embedding'] for row in ordered]
        if len(vectors) != len(texts) or any(len(v) != DIMENSION or any(not isinstance(x, (float,int)) for x in v) for v in vectors):
            raise ValueError('Embedding response dimension mismatch')
        return vectors
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=502, detail='Embedding provider failed or returned incompatible vectors') from exc
