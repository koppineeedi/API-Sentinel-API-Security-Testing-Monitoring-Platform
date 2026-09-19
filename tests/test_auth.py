import pytest

def test_user_registration_and_login(client):
    # Register user
    reg_response = client.post("/api/v1/auth/register", json={
        "email": "testuser@sentinel.com",
        "password": "SecurePassword123!",
        "full_name": "Test Security User",
        "role": "SECURITY_ANALYST"
    })
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert "access_token" in data
    assert data["email"] == "testuser@sentinel.com"

    # Login user
    login_response = client.post("/api/v1/auth/login", json={
        "email": "testuser@sentinel.com",
        "password": "SecurePassword123!"
    })
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    # Fetch current user
    me_response = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "testuser@sentinel.com"

def test_duplicate_registration_prevention(client):
    payload = {
        "email": "duplicate@sentinel.com",
        "password": "Password123!",
        "full_name": "Dup User"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"].lower()

def test_invalid_login_credentials(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@sentinel.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401
