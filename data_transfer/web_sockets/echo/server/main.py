from fastapi import FastAPI, WebSocket
import uvicorn

import random   
import time
import asyncio

async def get_random_data():  
    data = random.randint(1, 100)
    #time.sleep(1)
    await asyncio.sleep(10)
    return data


app = FastAPI()

# Bağlı istemcileri takip etmek için basit liste
connected_clients = []

@app.get("/")
async def root():
    return {"message": "WebSocket Sunucusu Çalışıyor", 
            "connected_clients": len(connected_clients)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Bağlantıyı kabul et
    await websocket.accept()
    # Bağlantıyı listeye ekle
    connected_clients.append(websocket)
    
    try:
        while True:
            # İstemciden mesaj bekle
            data = await websocket.receive_text()
            print(f"Alınan mesaj: {data}")

            data = await get_random_data()
            
            # İstemciye yanıt gönder
            await websocket.send_text(f"Mesajınız: {data}")
            print("Mesaj gönderildi.")
            
            # Diğer tüm istemcilere ilet
            for client in connected_clients:
                if client != websocket:  # Kendisi hariç
                    await client.send_text(f"Başka bir istemciden: {data}")
    
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        # Bağlantı kesildiğinde listeden çıkar
        if websocket in connected_clients:
            connected_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)