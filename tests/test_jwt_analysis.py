import pytest
import time
import jwt
from scanner.modules.jwt_scanner import JWTScanner
from scanner.base import ScannerContext, ScannerMode

def test_jwt_token_masking():
    raw_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    masked = JWTScanner.mask_token(raw_token)
    assert "[MASKED" in masked
    assert "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c" not in masked

def test_unsigned_jwt_algorithm_detection():
    # Construct unsigned token with 'alg: none'
    header = {"alg": "none", "typ": "JWT"}
    payload = {"sub": "user123", "email": "user@example.com"}
    token = jwt.encode(payload, "", algorithm="none")

    scanner = JWTScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.PASSIVE,
        auth_token_a=token
    )

    results = scanner.scan(context)
    rule_ids = [r.rule_id for r in results]
    assert "SEC-JWT-01" in rule_ids # 'alg: none' rule
    assert "SEC-JWT-02" in rule_ids # missing 'exp' rule

def test_jwt_excessive_expiration_detection():
    # Token expiring in 60 days
    future_exp = int(time.time()) + (60 * 86400)
    token = jwt.encode({"sub": "user123", "exp": future_exp}, "secret_key", algorithm="HS256")

    scanner = JWTScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.PASSIVE,
        auth_token_a=token
    )

    results = scanner.scan(context)
    rule_ids = [r.rule_id for r in results]
    assert "SEC-JWT-03" in rule_ids # Excessive expiration rule
