from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import numpy as np
import json
import asyncio
from datetime import datetime
import time

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print('data',data)
            
            if data == 'start':
                while True:
                    try:
                        stop_signal = await asyncio.wait_for(websocket.receive_text(), timeout=0.0001)
                        if stop_signal == 'stop':
                            break
                    except asyncio.TimeoutError:
                        pass
                    
                    # Generate 512 samples at 512 Hz
                    random_array = create_data_samples(sample_rate=512, duration_seconds=1)
                    print(len(random_array), datetime.now())
                    await websocket.send_text(json.dumps(random_array))

            elif data == 'show':
                random_array = await create_data_samples(sample_rate=512, duration_seconds=1)
                await websocket.send_text(json.dumps(random_array))

    except WebSocketDisconnect:
        print("Client disconnected")

def create_data_samples(sample_rate, duration_seconds):
    """
    Generate data samples at a specified sample rate (in Hz) for a given duration (in seconds).
    """
    num_samples = sample_rate * duration_seconds
    interval = 1.0 / sample_rate  # Interval between samples in seconds
    data = []

    start_time = time.time()
    for _ in range(num_samples):
        value = np.random.rand()
        timestamp = datetime.now().isoformat()
        data.append((value, timestamp))
        
        # Busy-wait loop to achieve precise timing
        while time.time() - start_time < interval:
            pass
        start_time += interval
    
    return data
