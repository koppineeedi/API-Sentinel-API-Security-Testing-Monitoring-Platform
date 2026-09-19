import pytest
from app.services.ai_provider import MockAIProvider, get_ai_provider

def get_auth_header(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "aianalyst@sentinel.com",
        "password": "Password123!",
        "full_name": "AI Security Analyst",
        "role": "SECURITY_ANALYST"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_mock_ai_provider_analyze_finding():
    provider = MockAIProvider()
    finding_data = {
        "title": "BOLA Endpoint Exposure",
        "severity": "HIGH",
        "evidence": "GET /api/users/102 returned 200 OK without scope match",
        "rule_id": "SEC-BOLA-01"
    }

    result = provider.analyze_finding(finding_data)
    assert result["model_used"] == "Sentinel-AI-MockEngine"
    assert result["risk_score"] == 8.5
    assert "Observed Evidence" in result["observed_evidence"] or "GET /api/users/102" in result["observed_evidence"]
    assert "Authoritative Rule [SEC-BOLA-01]" in result["detection_result"]
    assert "ai_interpretation" in result
    assert "ai_recommendation" in result

def test_mock_ai_provider_summary():
    provider = MockAIProvider()
    findings = [
        {"severity": "CRITICAL", "rule_id": "SEC-BOLA-01", "title": "BOLA Exposure"},
        {"severity": "HIGH", "rule_id": "SEC-AUTH-01", "title": "Missing JWT"}
    ]

    summary = provider.generate_summary(findings)
    assert summary["model_used"] == "Sentinel-AI-MockEngine"
    assert "1 Critical" in summary["executive_summary"]
    assert "BOLA" in summary["remediation_summary"]

def test_ai_router_endpoint(client):
    headers = get_auth_header(client)

    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={
        "name": "AI Target App",
        "target_url": "http://127.0.0.1:8000"
    }, headers=headers)
    proj_id = proj_res.json()["id"]

    # 2. Create Finding
    find_res = client.post("/api/v1/findings", json={
        "project_id": proj_id,
        "title": "BOLA on User Account Profile",
        "description": "User ID parameter lacks owner validation",
        "severity": "HIGH",
        "confidence": "HIGH",
        "status": "OPEN",
        "rule_id": "SEC-BOLA-01"
    }, headers=headers)
    finding_id = find_res.json()["id"]

    # 3. Analyze finding with AI
    res = client.post("/api/v1/ai/analyze", json={
        "finding_id": finding_id
    }, headers=headers)

    assert res.status_code == 201
    data = res.json()
    assert data["finding_id"] == finding_id
    assert "summary" in data
    assert "root_cause" in data
    assert "custom_remediation" in data
