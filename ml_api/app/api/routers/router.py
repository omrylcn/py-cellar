import importlib
from fastapi import APIRouter

from app.core.config import settings
from app.core.logging import logger_dict


logger = logger_dict["basic"]


# version 1
api_v1_router = APIRouter()

router_dict = {
    "clip": {"module": "app.api.routers.v1.clip", "router_name": "clip_router", "prefix": "/clip", "tags": ["clip"]},
    "qa": {"module": "app.api.routers.v1.qa", "router_name": "qa_router", "prefix": "/qa", "tags": ["qa"]},
}


def load_router(module_path, router_name):
    module = importlib.import_module(module_path)
    return getattr(module, router_name)


def include_enabled_routers():
    for key, router_info in router_dict.items():
        enable_setting = f"{key.upper()}_ENABLE"
        if hasattr(settings, enable_setting) and getattr(settings, enable_setting):
            router = load_router(router_info["module"], router_info["router_name"])
            api_v1_router.include_router(router, prefix=router_info["prefix"], tags=router_info["tags"])
            logger.info(f"Router '{key}' is enabled and loaded.")
        else:
            logger.info(f"Router '{key}' is not enabled or not configured properly.")


# Call the function to include enabled routers
include_enabled_routers()
