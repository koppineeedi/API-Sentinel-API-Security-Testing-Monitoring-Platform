import pytest
from scanner.orchestrator import SecurityScanner
from scanner.base import ScannerContext, ScannerMode, TargetEndpoint
from scanner.modules.header_scanner import HeaderScanner
from scanner.modules.input_validation_scanner import InputValidationScanner

def test_header_scanner_missing_headers():
    scanner = HeaderScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.PASSIVE,
        headers_to_test={"Server": "uvicorn"} # Missing HSTS, CSP, etc.
    )
    results = scanner.scan(context)
    assert len(results) >= 1
    assert results[0].rule_id == "SEC-HEAD-01"

def test_input_validation_scanner():
    scanner = InputValidationScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.PASSIVE,
        endpoints=[
            TargetEndpoint(path="/users/{user_id}", method="GET", parameters=None)
        ]
    )
    results = scanner.scan(context)
    assert len(results) >= 1
    assert results[0].rule_id == "SEC-INJ-01"
    assert "user_id" in results[0].evidence

def test_orchestrator_execution():
    orchestrator = SecurityScanner()
    context = ScannerContext(
        target_url="http://localhost:8000",
        mode=ScannerMode.PASSIVE,
        headers_to_test={"Server": "uvicorn"},
        endpoints=[
            TargetEndpoint(path="/api/v1/orders/{order_id}", method="POST")
        ]
    )
    results = orchestrator.run_all(context)
    assert isinstance(results, list)
    assert len(results) > 0
