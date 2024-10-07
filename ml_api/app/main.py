from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator,metrics
from prometheus_client import Counter

from app.api.routers.router import api_v1_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
intrumentator = Instrumentator()
intrumentator.add(metrics.default())
intrumentator.instrument(app).expose(app)

# Include routers
app.include_router(api_v1_router, prefix="/api/v1")


# example_counter = Counter('example_counter', 'Example Counter', ['value'])
# @app.get("/example")
# def example():
#     import random
#     value = random.randint(1, 10)
#     example_counter.labels(value=value).inc()
#     return {"message": "This is an example endpoint"}


@app.get("/")
async def root():
    return {"message": "Welcome to the ML API"}
