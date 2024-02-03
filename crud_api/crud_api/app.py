import uvicorn
from fastapi import FastAPI
from crud_api.routers import api_v1_router
from crud_api.config import API_V1_PREFIX

app = FastAPI(
    title="invamar API",

)


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(api_v1_router, prefix=API_V1_PREFIX)



# if __name__ == '__main__':
#     uvicorn.run("app:app", port=8080, host="0.0.0.0", reload=True)