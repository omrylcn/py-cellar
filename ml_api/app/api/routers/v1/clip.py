from fastapi import APIRouter


clip_router = APIRouter()

@clip_router.get("/info")
async def info():
    return {"message": "This is CLIP MODEL"}
