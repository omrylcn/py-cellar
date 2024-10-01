from fastapi import APIRouter
from app.core.config import settings

from app.api.routers.v1.clip import clip_router
from app.api.routers.v1.qa import qa_router

# version 1
api_v1_router = APIRouter()

router_dict = {
    "clip": {"router": clip_router, "prefix": "/clip", "tags": ["clip"]},
    "qa": {"router": qa_router, "prefix": "/qa", "tags": ["qa"]},
}

def include_enabled_routers():
    for key, router_info in router_dict.items():
        enable_setting = f"{key.upper()}_ENABLE"
        if hasattr(settings, enable_setting) and getattr(settings, enable_setting):
            api_v1_router.include_router(
                router_info["router"],
                prefix=router_info["prefix"],
                tags=router_info["tags"]
            )
        else:
            print(f"Router '{key}' is not enabled or not configured properly.")

# Call the function to include enabled routers
include_enabled_routers()