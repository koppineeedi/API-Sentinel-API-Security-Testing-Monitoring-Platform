import httpx
from typing import List, Dict
from scanner.base import BaseScanner, ScannerContext, ScannerResult

class HeaderScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "HeaderScanner"

    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        results: List[ScannerResult] = []
        target_url = context.target_url.rstrip("/")

        headers: Dict[str, str] = {}

        # 1. Use context headers if provided (e.g. from test or spec context)
        if context.headers_to_test:
            headers = {k.lower(): str(v) for k, v in context.headers_to_test.items()}
        else:
            # 2. Otherwise make passive HTTP request to target /health or root URL
            try:
                with httpx.Client(timeout=context.timeout_seconds, follow_redirects=False) as client:
                    resp = client.get(f"{target_url}/health")
                    headers = {k.lower(): str(v) for k, v in resp.headers.items()}
            except Exception:
                # Fallback empty headers if target server offline during passive test
                headers = {}

        missing = []
        if "strict-transport-security" not in headers:
            missing.append("Strict-Transport-Security (HSTS)")
        if "content-security-policy" not in headers:
            missing.append("Content-Security-Policy (CSP)")
        if "x-content-type-options" not in headers:
            missing.append("X-Content-Type-Options")
        if "referrer-policy" not in headers:
            missing.append("Referrer-Policy")
        if "cache-control" not in headers:
            missing.append("Cache-Control")

        if missing:
            results.append(ScannerResult(
                rule_id="SEC-HEAD-01",
                title="Missing Defensive Security Headers",
                severity="LOW",
                confidence="HIGH",
                endpoint="/",
                http_method="GET",
                description=f"Target environment responses are missing key security headers: {', '.join(missing)}.",
                evidence=f"Missing Headers: {', '.join(missing)}\nPresent Headers: {dict(headers)}",
                impact="Exposes application users to clickjacking, MIME sniffing, protocol downgrade attacks, and sensitive data caching.",
                remediation="Configure web gateway to return HSTS, CSP, X-Content-Type-Options, Referrer-Policy, and Cache-Control headers on all API responses."
            ))

        return results
