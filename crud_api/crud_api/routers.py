from fastapi import APIRouter
from crud_api.api import users_router
from crud_api.api import user_device_data_router
from crud_api.api import admin_router as admin
from crud_api.api import user_devices_router
from crud_api.api import roles_router
from crud_api.api import user_roles_router
from crud_api.api import company_router


# version 1
api_v1_router = APIRouter()
admin_router = APIRouter()


api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
api_v1_router.include_router(user_device_data_router, prefix="/user-device-data", tags=["user_device_data"])
api_v1_router.include_router(user_devices_router, prefix="/user-devices", tags=["user_devices"])
api_v1_router.include_router(roles_router, prefix="/roles", tags=["roles"])
api_v1_router.include_router(user_roles_router, prefix="/user-roles", tags=["user_roles"])
api_v1_router.include_router(company_router, prefix="/company", tags=["company"])
admin_router.include_router(admin, prefix="/admin", tags=["admin"])