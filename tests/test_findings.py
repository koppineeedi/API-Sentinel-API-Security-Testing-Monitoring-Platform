import pytest

def get_auth_header(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "secsec@sentinel.com",
        "password": "Password123!",
        "full_name": "Security Analyst",
        "role": "SECURITY_ANALYST"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_findings_workflow(client):
    headers = get_auth_header(client)

    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={
        "name": "Target App",
        "target_url": "http://127.0.0.1:8000"
    }, headers=headers)
    proj_id = proj_res.json()["id"]

    # 2. Create Finding
    find_res = client.post("/api/v1/findings", json={
        "project_id": proj_id,
        "title": "BOLA on User Account Profile",
        "description": "User ID parameter lacks owner validation",
        "severity": "CRITICAL",
        "confidence": "HIGH",
        "status": "OPEN",
        "rule_id": "SEC-BOLA-01",
        "remediation": "Validate user session token ownership"
    }, headers=headers)
    assert find_res.status_code == 201
    finding = find_res.json()
    finding_id = finding["id"]
    assert finding["status"] == "OPEN"
    assert finding["severity"] == "CRITICAL"

    # 3. Update Finding Status to RESOLVED
    update_res = client.patch(f"/api/v1/findings/{finding_id}", json={
        "status": "RESOLVED"
    }, headers=headers)
    assert update_res.status_code == 200
    updated_finding = update_res.json()
    assert updated_finding["status"] == "RESOLVED"
    assert updated_finding["resolved_at"] is not None

    # 4. Filter Findings by Severity
    filter_res = client.get("/api/v1/findings?severity=CRITICAL", headers=headers)
    assert filter_res.status_code == 200
    assert len(filter_res.json()) >= 1
