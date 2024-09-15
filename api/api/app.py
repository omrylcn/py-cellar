from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from api.routers import api_v1_router, admin_router
from api.config import API_V1_PREFIX

app = FastAPI(
    title="CRUD API",
)


html_content = """
<!DOCTYPE html>
<html>
    <head>
        <title>CRUD API</title>
    </head>
    <body>
        <h1>CRUD API</h1>
        <p>Welcome to the 'CRUD API Template'. This is a API that allows you to manage your inventory.</p>
        <p>Click <a href="/docs">here</a> to view the API documentation.</p>
    </body>
</html>
"""


@app.get("/", tags=["root"])
async def root():
    return HTMLResponse(content=html_content, status_code=200)


app.include_router(api_v1_router, prefix=API_V1_PREFIX)
app.include_router(admin_router)
