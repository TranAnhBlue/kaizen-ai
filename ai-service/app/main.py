from fastapi import FastAPI
from app.api.routes.analytics import router as analytics_router
from app.api.routes.ai import router as ai_router
app = FastAPI(title='Kaizen AI Internal Service', docs_url=None, redoc_url=None)
app.include_router(analytics_router)
app.include_router(ai_router)
@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'kaizen-ai'}
