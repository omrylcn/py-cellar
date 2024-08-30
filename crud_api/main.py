import uvicorn
from argparse import ArgumentParser
from crud_api.app import app

parser = ArgumentParser()

parser.add_argument('--port', type=int, default=8080, help='port to run the server on')
parser.add_argument('--host', type=str, default="0.0.0.0", help='host to run the server on')
parser.add_argument('--reload', type=bool, default=False, help='reload the server on change')

args = parser.parse_args()

if __name__ == '__main__':
    uvicorn.run("crud_api.app:app", port=args.port,host=args.host,reload=args.reload)

