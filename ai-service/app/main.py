from fastapi import FastAPI
from app.api.routes.analytics import router as analytics_router
from app.api.routes.ai import router as ai_router
from app.api.routes.rag import router as rag_router
from app.api.routes.forecasting import router as forecasting_router
from app.api.routes.recommendations import router as recommendations_router
app = FastAPI(title='Kaizen AI Internal Service', docs_url=None, redoc_url=None)
app.include_router(analytics_router)
app.include_router(ai_router)
app.include_router(rag_router)
app.include_router(forecasting_router)
app.include_router(recommendations_router)
@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'kaizen-ai'}
