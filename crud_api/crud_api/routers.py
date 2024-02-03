from fastapi import APIRouter
from crud_api.api import users_router


# version 1
api_v1_router = APIRouter()


api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
