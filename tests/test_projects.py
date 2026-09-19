import pytest

def get_auth_header(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "projadmin@sentinel.com",
        "password": "Password123!",
        "full_name": "Project Admin",
        "role": "ADMIN"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_project_and_endpoint_crud(client):
    headers = get_auth_header(client)

    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={
        "name": "Auth Lab Service",
        "description": "Intentionally vulnerable auth lab",
        "target_url": "http://127.0.0.1:8000"
    }, headers=headers)
    assert proj_res.status_code == 201
    proj = proj_res.json()
    proj_id = proj["id"]

    # 2. Add Endpoint
    ep_res = client.post("/api/v1/endpoints", json={
        "project_id": proj_id,
        "path": "/api/v1/users/{id}",
        "method": "GET",
        "description": "User Lookup Endpoint"
    }, headers=headers)
    assert ep_res.status_code == 201
    ep = ep_res.json()
    assert ep["path"] == "/api/v1/users/{id}"

    # 3. List Endpoints for Project
    list_ep_res = client.get(f"/api/v1/endpoints?project_id={proj_id}", headers=headers)
    assert list_ep_res.status_code == 200
    assert len(list_ep_res.json()) == 1
