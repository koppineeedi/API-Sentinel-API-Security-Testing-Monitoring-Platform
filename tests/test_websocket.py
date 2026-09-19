import pytest
from fastapi.testclient import TestClient

def test_websocket_traffic_stream(client):
    with client.websocket_connect("/api/v1/ws/traffic") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_json()
        assert data["type"] == "pong"
