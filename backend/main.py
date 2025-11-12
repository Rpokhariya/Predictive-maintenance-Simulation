import uvicorn
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sod_logic import RealTimeSoDProcessor

app = FastAPI()

# Allow all origins for simplicity. 
# You can restrict this later to your Netlify URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the full dataset into memory once
try:
    with open('kurtosis_data.json', 'r') as f:
        all_data = json.load(f)
    print("Kurtosis data loaded successfully.")
except FileNotFoundError:
    print("FATAL: kurtosis_data.json not found. Please run preprocess.py first.")
    all_data = {}

@app.websocket("/ws/{test_set}/{bearing_name}")
async def websocket_endpoint(websocket: WebSocket, test_set: str, bearing_name: str):
    """
    WebSocket endpoint that streams SoD data one point at a time.
    """
    await websocket.accept()
    
    # Get the specific data series
    try:
        # FastAPI un-escapes URL characters, so 'B1-Ch1 (Healthy)'
        # becomes 'B1-Ch1 (Healthy)'. This is fine.
        raw_series = all_data[test_set][bearing_name]
        total_data_len = len(raw_series)
    except KeyError:
        print(f"Data not found for {test_set} / {bearing_name}")
        await websocket.close(code=1008, reason="Data not found")
        return

    # Create a NEW processor for this specific client
    processor = RealTimeSoDProcessor(
        baseline_frac=0.2, 
        smooth_window=50, 
        sigma_factor=2.0, 
        persistence_count=50
    )

    try:
        # Loop through the historical data as a "live" stream
        for raw_value in raw_series:
            # 1. Process the point (calculates smooth, checks SoD)
            data_point = processor.process_point(raw_value, total_data_len)
            
            # 2. Push the JSON data packet to the client
            await websocket.send_json(data_point)
            
            # 3. Control simulation speed (20ms = 50 points/sec)
            await asyncio.sleep(0.02) 
            
        await websocket.send_json({"status": "Finished"})

    except WebSocketDisconnect:
        print(f"Client disconnected from {test_set}/{bearing_name}")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.close(code=1011, reason=f"An error occurred: {e}")

if __name__ == "__main__":
    print("Starting FastAPI server on http://localhost:8000")
    # This runs the server. For production, you'll deploy differently (e.g., on Render).
    uvicorn.run(app, host="0.0.0.0", port=8000)