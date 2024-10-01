# # from fastapi import APIRouter
# # from api.api import users_router
# # from api.api import user_data_router
# # from api.api import admin_router as admin


# # # version 1
# # api_v1_router = APIRouter()
# # admin_router = APIRouter()


# # api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
# # api_v1_router.include_router(user_data_router, prefix="/user-device-data", tags=["user_device_data"])
# # admin_router.include_router(admin, prefix="/admin", tags=["admin"])


# from fastapi import APIRouter
# from app.api.routers.v1.clip import clip_router
# from app.api.routers.v1.qa import qa_router
# from app.core.config import settings


# # version 1
# api_v1_router = APIRouter()


# router_dict = {
#     "clip": {"router": clip_router, "prefix": "/clip", "tags": ["clip"]},
#     "qa": {"router": qa_router, "prefix": "/qa", "tags": ["qa"]},
# }



# for key in router_dict.keys():
#     key_ = key.upper()+"_ENABLE"
#     res = getattr(settings, key_)
#     if res:
#         api_v1_router.include_router(router_dict[key]["router"], prefix=router_dict[key]["prefix"], tags=router_dict[key]["tags"])



# # api_v1_router.include_router(clip_router, prefix="/clip", tags=["clip"])
# # api_v1_router.include_router(qa_router, prefix="/qa", tags=["qa"])
