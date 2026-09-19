import pytest

def get_auth_token(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "trafficuser@sentinel.com",
        "password": "Password123!",
        "full_name": "Traffic Analyst",
        "role": "SECURITY_ANALYST"
    })
    return res.json()["access_token"]

def test_traffic_ingestion_and_analytics(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={
        "name": "Traffic Test Project",
        "target_url": "http://localhost:8000"
    }, headers=headers)
    proj_id = proj_res.json()["id"]

    # 2. Ingest Traffic Event
    event_payload = {
        "project_id": proj_id,
        "request_method": "POST",
        "request_url": "/api/v1/users",
        "response_status": 201,
        "response_time_ms": 145.5,
        "request_size_bytes": 128,
        "response_size_bytes": 512,
        "client_ip": "10.0.0.5"
    }
    ingest_res = client.post("/api/v1/traffic", json=event_payload, headers=headers)
    assert ingest_res.status_code == 201
    event = ingest_res.json()
    assert event["response_status"] == 201
    assert event["request_size_bytes"] == 128

    # 3. Query Endpoint Stats
    ep_stats_res = client.get(f"/api/v1/traffic/stats/endpoints?project_id={proj_id}", headers=headers)
    assert ep_stats_res.status_code == 200
    ep_stats = ep_stats_res.json()
    assert len(ep_stats) == 1
    assert ep_stats[0]["path"] == "/api/v1/users"

    # 4. Query Status Code Stats
    sc_stats_res = client.get(f"/api/v1/traffic/stats/status-codes?project_id={proj_id}", headers=headers)
    assert sc_stats_res.status_code == 200
    sc_stats = sc_stats_res.json()
    c2xx = next(s for s in sc_stats if s["status_code_group"] == "2xx")
    assert c2xx["count"] == 1
