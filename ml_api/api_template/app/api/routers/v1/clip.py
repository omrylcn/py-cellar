# from fastapi import APIRouter, UploadFile, File
# from app.services.clip_service import CLIPService
# from app.schemas.clip import CLIPResponse

# router = APIRouter()
# clip_service = CLIPService()

# @router.post("/predict", response_model=CLIPResponse)
# async def predict_clip(file: UploadFile = File(...)):
#     result = await clip_service.predict(file)
#     return result

from fastapi import APIRouter


router = APIRouter()



@router.get("/info")
async def info():
    return {"message": "This is CLIP MODEL"}
