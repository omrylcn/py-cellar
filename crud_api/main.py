import uvicorn
from crud_api.app import app

if __name__ == '__main__':
    uvicorn.run(app, port=8080, host="0.0.0.0")
