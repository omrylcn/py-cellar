from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routers.router import api_v1_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the ML API"}
