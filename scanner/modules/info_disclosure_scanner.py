import httpx
from typing import List
from scanner.base import BaseScanner, ScannerContext, ScannerResult

DISCLOSURE_HEADERS = ["server", "x-powered-by", "x-aspnet-version", "x-generator", "x-backend-server"]

class InformationDisclosureScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "InformationDisclosureScanner"

    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        results: List[ScannerResult] = []
        target_url = context.target_url.rstrip("/")

        try:
            with httpx.Client(timeout=context.timeout_seconds, follow_redirects=False) as client:
                # 1. Inspect headers for server version disclosure
                resp = client.get(f"{target_url}/health")
                headers = {k.lower(): v for k, v in resp.headers.items()}

                disclosed = []
                for h in DISCLOSURE_HEADERS:
                    if h in headers:
                        disclosed.append(f"{h}: {headers[h]}")

                if disclosed:
                    results.append(ScannerResult(
                        rule_id="SEC-INFO-01",
                        title="Server Information & Technology Disclosure Headers",
                        severity="LOW",
                        confidence="HIGH",
                        endpoint="/health",
                        http_method="GET",
                        description=f"HTTP response reveals specific technology stack details in headers: {', '.join(disclosed)}.",
                        evidence=f"Disclosed Headers: {', '.join(disclosed)}",
                        impact="Aids attackers in fingerprinting server frameworks and identifying known CVE vulnerabilities.",
                        remediation="Remove or sanitize Server and X-Powered-By response headers at the API gateway."
                    ))

                # 2. Check 404 / 500 error pages for stack traces or internal leaks
                err_resp = client.get(f"{target_url}/nonexistent_sentinel_path_404")
                body = err_resp.text.lower()
                if any(kw in body for kw in ["traceback (most recent call last)", "exception in thread", "stack trace", "at com.", "fatal error in"]):
                    results.append(ScannerResult(
                        rule_id="SEC-INFO-02",
                        title="Verbose Error Message & Stack Trace Leakage",
                        severity="MEDIUM",
                        confidence="HIGH",
                        endpoint="/nonexistent_sentinel_path_404",
                        http_method="GET",
                        description="Application error responses leak internal stack traces or framework debug details.",
                        evidence=f"HTTP {err_resp.status_code}\nSnippet: {err_resp.text[:300]}",
                        impact="Exposes internal file paths, code logic, and dependency versions to unauthorized users.",
                        remediation="Disable debug mode in production and implement custom global exception handlers returning sanitized error objects."
                    ))
        except Exception:
            pass

        return results
