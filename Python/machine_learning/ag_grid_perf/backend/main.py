import asyncio
import json
import random
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONNECTIONS: List[WebSocket] = []

def generate_stock_data(row_count: int):
    data = []
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "FB", "NVDA", "NFLX", "INTC", "AMD"]
    sectors = ["Technology", "Finance", "Healthcare", "Energy", "Consumer"]
    regions = ["North America", "Europe", "Asia-Pacific"]
    
    for i in range(row_count):
        ticker = tickers[i % len(tickers)]
        sector = sectors[i % len(sectors)]
        region = regions[i % len(regions)]
        
        data.append({
            "id": i,
            "ticker": f"{ticker}-{i}",
            "sector": sector,
            "region": region,
            "price": round(random.uniform(100, 2000), 2),
            "volume": random.randint(1000, 1000000),
            "change": round(random.uniform(-5, 5), 2),
            "last_updated": time.time()
        })
    return data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    CONNECTIONS.append(websocket)
    try:
        # Wait for initialization message
        init_msg = await websocket.receive_text()
        init_data = json.loads(init_msg)
        row_count = int(init_data.get("rowCount", 100))
        # Default 50ms (20 updates/sec)
        frequency_ms = int(init_data.get("frequency", 50)) 
        sleep_time = frequency_ms / 1000.0
        
        print(f"Client requested {row_count} rows at {frequency_ms}ms interval")

        # Send initial dataset
        initial_data = generate_stock_data(row_count)
        print(f"Sending initial data: {len(initial_data)} rows")
        await websocket.send_json({"type": "initial", "data": initial_data})
        
        # Give client a moment to render initial data before flooding updates
        await asyncio.sleep(0.5)

        # Start simulation loop
        while True:
            # Simulate updates for a subset of the data
            current_time = time.time()
            updates = []
            
            # Update 10% of the rows or max 500 rows per tick to simulate frequent market moves
            num_updates = min(int(row_count * 0.1), 1000)
            if num_updates < 1: num_updates = 1
            
            indices_to_update = random.sample(range(row_count), num_updates)
            
            for idx in indices_to_update:
                ticker_base = initial_data[idx]["ticker"].split('-')[0]
                new_price = initial_data[idx]["price"] + random.uniform(-2, 2)
                updates.append({
                    "id": idx,
                    "ticker": initial_data[idx]["ticker"],
                    "sector": initial_data[idx]["sector"], # Send static fields to simulate full row update if needed
                    "region": initial_data[idx]["region"],
                    "price": round(new_price, 2),
                    "volume": initial_data[idx]["volume"] + random.randint(10, 500),
                    "change": round(random.uniform(-5, 5), 2),
                    "last_updated": current_time
                })
                # Update our local state to keep consistency mostly sane
                initial_data[idx]["price"] = new_price

            await websocket.send_json({"type": "update", "data": updates})
            await asyncio.sleep(sleep_time)

    except WebSocketDisconnect:
        print("Client disconnected")
        CONNECTIONS.remove(websocket)
    except Exception as e:
        print(f"Error: {e}")
        CONNECTIONS.remove(websocket)
