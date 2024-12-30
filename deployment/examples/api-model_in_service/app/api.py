from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response,HTMLResponse
import onnxruntime
import numpy as np
from PIL import Image
import io

from app.service import ImageService

app = FastAPI()
image_service = ImageService()

# Initialize ONNX Runtime session


@app.post("/process-image/")
async def process_image_endpoint(
    file: UploadFile = File(...),
    image_size: int = 224,
):
    """
    Endpoint to process an uploaded image
    """
    try:

        # Process the image
        processed_image = await image_service.infer(file, image_size=image_size)

        # Convert the processed image to bytes
        img_byte_arr = io.BytesIO()
        processed_image.save(img_byte_arr, format=processed_image.format or "PNG")
        img_byte_arr = img_byte_arr.getvalue()

        # Return the processed image
        return Response(
            content=img_byte_arr,
            media_type=f"image/{processed_image.format.lower() if processed_image.format else 'png'}",
        )

    except Exception as e:
        return {"error": str(e)}



@app.get("/")
def read_root():
    return HTMLResponse("""
        <html>
            <head>
                <title>Image Processing</title>
            </head>
            <body>
                <h1>Image Processing API</h1>
                <p>Send POST request to /process-image/ with an image file to process it.</p>
            </body>
        </html>
    """)