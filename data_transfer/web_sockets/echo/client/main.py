from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import websockets
import asyncio

app = FastAPI()

# HTML sayfa içeriği
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket İstemcisi</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Gönder</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# Basit bir API endpoint'i ile WebSocket mesajı gönderme
@app.get("/send/{message}")
async def send_message(message: str):
    try:
        # Sunucuya WebSocket bağlantısı kur
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            # Mesaj gönder
            await websocket.send(message)
            # Yanıtı al
            response = await websocket.recv()
            return {"sent": message, "response": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("client:app", host="0.0.0.0", port=8002, reload=True)