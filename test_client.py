from fastapi.testclient import TestClient
from core import app


import websockets
import asyncio
client = TestClient(app)
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "active"} 
    
async def test():
    async with websockets.connect("ws://localhost:8000/ws/session") as ws:
        for _ in range(3):
            print(await ws.recv())

asyncio.run(test())

# import pytest
# from fastapi.testclient import TestClient
# from core import app
# import os
# import asyncio
# from httpx import AsyncClient

# client = TestClient(app)

# def test_health_check():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"status": "active"}  # Updated status message

# @pytest.mark.asyncio
# async def test_websocket_flow():
#     # Test WebSocket connection using async client
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         async with ac.websocket_connect("/ws/session/test") as websocket:
#             # Initial connection check
#             data = await websocket.receive_json()
#             assert isinstance(data, dict)
            
#             # Validate response structure
#             assert "screen_text" in data
#             assert "logs" in data
#             assert "analysis" in data
            
#             # Type checks
#             assert isinstance(data["screen_text"], str)
#             assert isinstance(data["logs"], list)
#             assert isinstance(data["analysis"], str)

#             # Test multiple messages
#             for _ in range(3):
#                 data = await websocket.receive_json()
#                 assert all(key in data for key in ["screen_text", "logs", "analysis"])
