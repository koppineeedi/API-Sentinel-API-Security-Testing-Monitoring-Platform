import pytest

def get_auth_token(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "lifecycleuser@sentinel.com",
        "password": "Password123!",
        "full_name": "Lifecycle Analyst",
        "role": "SECURITY_ANALYST"
    })
    return res.json()["access_token"]

def test_finding_lifecycle_and_audit(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Project & Finding
    proj_res = client.post("/api/v1/projects", json={
        "name": "Lifecycle Test Project",
        "target_url": "http://localhost:8000"
    }, headers=headers)
    proj_id = proj_res.json()["id"]

    finding_res = client.post("/api/v1/findings", json={
        "project_id": proj_id,
        "title": "BOLA Profile Leak",
        "severity": "HIGH",
        "confidence": "HIGH",
        "status": "OPEN"
    }, headers=headers)
    finding_id = finding_res.json()["id"]

    # 2. Confirm Finding
    confirm_res = client.post(f"/api/v1/findings/{finding_id}/confirm", headers=headers)
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "CONFIRMED"

    # 3. Mark False Positive
    fp_res = client.post(f"/api/v1/findings/{finding_id}/false-positive", headers=headers)
    assert fp_res.status_code == 200
    assert fp_res.json()["status"] == "FALSE_POSITIVE"

    # 4. Resolve Finding
    resolve_res = client.post(f"/api/v1/findings/{finding_id}/resolve", headers=headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

    # 5. Reopen Finding
    reopen_res = client.post(f"/api/v1/findings/{finding_id}/reopen", headers=headers)
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "OPEN"

    # 6. Verify Audit Log Recorded
    audit_res = client.get("/api/v1/audit", headers=headers)
    assert audit_res.status_code == 200
    actions = [a["action"] for a in audit_res.json()]
    assert "FINDING_STATUS_CHANGE" in actions
