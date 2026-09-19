import pytest
from app.security.ssrf import SSRFProtector

def test_valid_public_url():
    url = "https://example.com/openapi.json"
    res = SSRFProtector.validate_url(url, allow_local=False)
    assert res == url

def test_invalid_scheme():
    with pytest.raises(ValueError, match="Disallowed URL scheme"):
        SSRFProtector.validate_url("file:///etc/passwd")

def test_private_ip_ssrf_prevention():
    # Loopback IP without allow_local should raise SSRF violation
    with pytest.raises(ValueError, match="SSRF Security Violation"):
        SSRFProtector.validate_url("http://127.0.0.1:8000/spec", allow_local=False)

    # AWS IMDS metadata IP should raise SSRF violation
    with pytest.raises(ValueError, match="SSRF Security Violation"):
        SSRFProtector.validate_url("http://169.254.169.254/latest/meta-data/", allow_local=False)

def test_allow_local_override():
    # Local loopback allowed for authorized local lab testing
    url = "http://localhost:8000/docs"
    res = SSRFProtector.validate_url(url, allow_local=True)
    assert res == url
