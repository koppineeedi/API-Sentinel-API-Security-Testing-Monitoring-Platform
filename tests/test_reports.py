import pytest

def get_auth_header(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "reportanalyst@sentinel.com",
        "password": "Password123!",
        "full_name": "Report Security Analyst",
        "role": "SECURITY_ANALYST"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_secret_redaction():
    from app.services.report_service import ReportGenerator
    raw_text = (
        'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c\n'
        '{"password": "MySuperSecretPassword123!", "api_key": "secret-key-999"}\n'
        '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----'
    )
    sanitized = ReportGenerator.sanitize_secrets(raw_text)

    assert "MySuperSecretPassword123!" not in sanitized
    assert "[REDACTED_PASSWORD]" in sanitized
    assert "secret-key-999" not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized
    assert "MIIEowIBAAKCAQEA0" not in sanitized

def test_report_generation_endpoint(client):
    headers = get_auth_header(client)

    # 1. Create Project
    proj_res = client.post("/api/v1/projects", json={
        "name": "Report Audit Target",
        "target_url": "http://127.0.0.1:8000"
    }, headers=headers)
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Generate Report
    res = client.post("/api/v1/reports", json={
        "project_id": proj_id,
        "title": "Executive OWASP Security Report",
        "report_type": "EXECUTIVE",
        "format": "HTML"
    }, headers=headers)

    assert res.status_code == 201
    report = res.json()
    assert report["title"] == "Executive OWASP Security Report"
    assert report["format"] == "HTML"

    report_id = report["id"]

    # 3. Test HTML download endpoint
    html_res = client.get(f"/api/v1/reports/{report_id}/download/html", headers=headers)
    assert html_res.status_code == 200
    assert "<html" in html_res.text.lower()
    assert "Executive OWASP Security Report" in html_res.text

    # 4. Test PDF download endpoint
    pdf_res = client.get(f"/api/v1/reports/{report_id}/download/pdf", headers=headers)
    assert pdf_res.status_code == 200
