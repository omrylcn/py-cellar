from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response, HTMLResponse
from celery.result import AsyncResult
from app.service import process_image_task
from app.config import settings

app = FastAPI(title="Model Service API")

@app.post("/process-image/")
async def process_image_endpoint(
    file: UploadFile = File(...),
    image_size: int = settings.MODEL_SIZE,
):
    content = await file.read()
    task = process_image_task.delay(content, (image_size, image_size))
    return {"task_id": task.id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Check the status of a processing task"""
    result = AsyncResult(task_id)
    if result.ready():
        if result.successful():
            return {"status": "completed"}
        else:
            return {"status": "failed", "error": str(result.result)}
    return {"status": "processing"}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """Get the processed image for a completed task"""
    result = AsyncResult(task_id)
    if not result.ready():
        return {"error": "Task still processing"}
    
    if result.successful():
        return Response(
            content=result.get(),
            media_type="image/png"
        )
    return {"error": "Task failed"}

@app.get("/", response_class=HTMLResponse)
def get_root():
    return """
        <html>
            <head>
                <title>Image Processing</title>
            </head>
            <body>
                <h1>Image Processing API</h1>
                <p>Send POST request to /process-image/ with an image file to process it.</p>
            </body>
        </html>
    """