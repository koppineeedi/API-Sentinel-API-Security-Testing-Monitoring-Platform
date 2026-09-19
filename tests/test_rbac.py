import pytest

def get_auth_token(client, email, role):
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": f"User {role}",
        "role": role
    })
    return res.json()["access_token"]

def test_rbac_permissions(client):
    # First registered user becomes ADMIN
    admin_token = get_auth_token(client, "admin@test.com", "ADMIN")
    analyst_token = get_auth_token(client, "analyst@test.com", "SECURITY_ANALYST")
    viewer_token = get_auth_token(client, "viewer@test.com", "VIEWER")

    # 1. Admin Endpoint (/api/v1/users)
    # Admin can list users
    res_admin = client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200

    # Viewer CANNOT list users (Forbidden 403)
    res_viewer = client.get("/api/v1/users", headers={"Authorization": f"Bearer {viewer_token}"})
    assert res_viewer.status_code == 403

    # 2. Project Creation (/api/v1/projects)
    # Analyst can create projects
    res_analyst_proj = client.post("/api/v1/projects", json={
        "name": "Analyst Staging API",
        "target_url": "http://staging.api.local"
    }, headers={"Authorization": f"Bearer {analyst_token}"})
    assert res_analyst_proj.status_code == 201

    # Viewer CANNOT create project (Forbidden 403)
    res_viewer_proj = client.post("/api/v1/projects", json={
        "name": "Viewer Proj",
        "target_url": "http://invalid.local"
    }, headers={"Authorization": f"Bearer {viewer_token}"})
    assert res_viewer_proj.status_code == 403

    # Viewer CAN view projects (Read-only 200)
    res_viewer_get_proj = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {viewer_token}"})
    assert res_viewer_get_proj.status_code == 200
    assert len(res_viewer_get_proj.json()) >= 1
