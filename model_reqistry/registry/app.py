"""
REST API endpoints for the Model Registry service.

This module provides FastAPI routes for interacting with the model registry,
including uploading models and their metadata.

Notes
-----
The API uses FastAPI for routing and request handling, and supports
multipart/form-data for file uploads along with JSON metadata.
"""


from typing import Optional, Dict
import io
import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile, status
from fastapi.responses import StreamingResponse, JSONResponse,FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .logger import logger
from .api.routes.models import app as api
from .version import __version__

BASE_DIR = Path(__file__).resolve().parent
logger.info(f"{__version__}")

app = FastAPI(
    title="Model Registry API",
    description="REST API for managing ML models and their metadata",
    version= __version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api,prefix="")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
@app.get("/")
async def root():
    return FileResponse(str(BASE_DIR / "static" / "index.html"))
   

