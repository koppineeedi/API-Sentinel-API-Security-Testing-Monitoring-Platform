import pytest
from scanner.modules.authorization_scanner import AuthorizationScanner
from scanner.base import ScannerContext, ScannerMode, TargetEndpoint

def test_bola_passive_mode_skipped():
    scanner = AuthorizationScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.PASSIVE,
        auth_token_a="token_a",
        auth_token_b="token_b",
        bola_target_id="42"
    )
    # BOLA testing must not run in PASSIVE mode
    results = scanner.scan(context)
    assert len(results) == 0

def test_bola_unconfigured_skipped():
    scanner = AuthorizationScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.ACTIVE_AUTHORIZED,
        auth_token_a=None # Missing explicit token configuration
    )
    results = scanner.scan(context)
    assert len(results) == 0
