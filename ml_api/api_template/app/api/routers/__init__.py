# from fastapi import APIRouter
# from api.api import users_router
# from api.api import user_data_router
# from api.api import admin_router as admin


# # version 1
# api_v1_router = APIRouter()
# admin_router = APIRouter()


# api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
# api_v1_router.include_router(user_data_router, prefix="/user-device-data", tags=["user_device_data"])
# admin_router.include_router(admin, prefix="/admin", tags=["admin"])


from fastapi import APIRouter
from app.api.routers.v1.clip import router as clip_router




# version 1 

api_v1_router = APIRouter()
api_v1_router.include_router(clip_router, prefix="/clip", tags=["clip"])