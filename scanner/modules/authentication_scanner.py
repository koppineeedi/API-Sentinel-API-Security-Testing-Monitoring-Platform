import httpx
from typing import List
from scanner.base import BaseScanner, ScannerContext, ScannerResult, ScannerMode

class AuthenticationScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "AuthenticationScanner"

    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        results: List[ScannerResult] = []
        target_url = context.target_url.rstrip("/")

        # In PASSIVE mode, analyze spec endpoints missing security annotations
        for ep in context.endpoints:
            if ep.method.upper() in ["POST", "PUT", "DELETE", "PATCH"]:
                # Check if endpoint lacks authorization headers in specs or context
                if not ep.headers or not any(h.lower() in ["authorization", "x-api-key"] for h in ep.headers.keys()):
                    results.append(ScannerResult(
                        rule_id="SEC-AUTH-01",
                        title=f"Potentially Unauthenticated State-Changing Endpoint ({ep.method} {ep.path})",
                        severity="MEDIUM",
                        confidence="MEDIUM",
                        endpoint=ep.path,
                        http_method=ep.method,
                        description=f"State-modifying endpoint '{ep.method} {ep.path}' has no security requirements specified.",
                        evidence=f"Method: {ep.method}\nPath: {ep.path}\nSecurity Headers: None",
                        impact="Allows unauthorized users to mutate database records or trigger side-effects.",
                        remediation="Enforce authentication middleware on all state-changing endpoints."
                    ))

        # In ACTIVE_AUTHORIZED mode, send controlled invalid/malformed token requests to verify 401 response
        if context.mode == ScannerMode.ACTIVE_AUTHORIZED and context.endpoints:
            try:
                with httpx.Client(timeout=context.timeout_seconds, follow_redirects=False) as client:
                    sample_ep = context.endpoints[0]
                    test_url = f"{target_url}{sample_ep.path}"

                    # Test 1: Request with no auth header
                    resp_no_auth = client.get(test_url)
                    if resp_no_auth.status_code == 200:
                        results.append(ScannerResult(
                            rule_id="SEC-AUTH-02",
                            title=f"Protected Endpoint Accessible Without Authentication ({sample_ep.path})",
                            severity="HIGH",
                            confidence="HIGH",
                            endpoint=sample_ep.path,
                            http_method="GET",
                            description="Endpoint returned HTTP 200 OK when accessed without any authorization header.",
                            evidence=f"GET {test_url} -> HTTP {resp_no_auth.status_code}",
                            impact="Completely bypasses authentication controls.",
                            remediation="Ensure authentication guards return HTTP 401 Unauthorized for unauthenticated requests."
                        ))

                    # Test 2: Request with malformed token
                    resp_malformed = client.get(test_url, headers={"Authorization": "Bearer malformed_invalid_jwt_token_xyz"})
                    if resp_malformed.status_code not in [401, 403]:
                        results.append(ScannerResult(
                            rule_id="SEC-AUTH-03",
                            title=f"Inconsistent Malformed Token Handling ({sample_ep.path})",
                            severity="MEDIUM",
                            confidence="HIGH",
                            endpoint=sample_ep.path,
                            http_method="GET",
                            description=f"Endpoint responded with HTTP {resp_malformed.status_code} instead of HTTP 401 for malformed token.",
                            evidence=f"Authorization: Bearer malformed_invalid_jwt_token_xyz -> HTTP {resp_malformed.status_code}",
                            impact="Inconsistent token validation behavior across API routes.",
                            remediation="Standardize authentication error responses to return HTTP 401 Unauthorized."
                        ))
            except Exception:
                pass

        return results
