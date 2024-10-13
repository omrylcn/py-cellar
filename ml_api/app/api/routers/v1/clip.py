from fastapi import APIRouter, UploadFile, File
from app.services.clip import CLIPService
from app.schemas.clip import CLIPResponse

clip_router = APIRouter()
clip_service = CLIPService()

@clip_router.post("/predict", response_model=CLIPResponse)
async def predict_image(file: UploadFile = File(...), labels: list[str] = ["a photo of a cat", "a photo of a dog"]):
    result = clip_service.predict(file, labels)
    return result

# Usage example
# import requests
# url = "http://your-fastapi-server/predict"
# files = {"file": ("image.jpg", open("path/to/image.jpg", "rb"), "image/jpeg")}
# data = {"labels": ["a photo of a cat", "a photo of a dog"]}
# response = requests.post(url, files=files, data=data)
# print(response.json())