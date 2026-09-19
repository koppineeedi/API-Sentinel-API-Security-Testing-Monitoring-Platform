import pytest
from scanner.modules.rate_limit_scanner import RateLimitScanner
from scanner.base import ScannerContext, ScannerMode

def test_rate_limit_passive_mode_skipped():
    scanner = RateLimitScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.PASSIVE
    )
    # Rate limit active burst must not execute in PASSIVE mode
    results = scanner.scan(context)
    assert len(results) == 0
