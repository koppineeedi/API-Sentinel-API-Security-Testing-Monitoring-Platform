import time
import httpx
from typing import List
from scanner.base import BaseScanner, ScannerContext, ScannerResult, ScannerMode

class RateLimitScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "RateLimitScanner"

    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        results: List[ScannerResult] = []

        # Controlled rate limiting analysis requires ACTIVE_AUTHORIZED mode
        if context.mode != ScannerMode.ACTIVE_AUTHORIZED:
            return results

        target_url = context.target_url.rstrip("/")

        # Controlled small request burst (e.g. 10 requests max to avoid DoS)
        burst_count = min(context.max_burst_requests, 15)
        auth_endpoint = "/api/v1/auth/login"
        full_url = f"{target_url}{auth_endpoint}"

        try:
            status_codes = []
            has_rate_limit_headers = False

            with httpx.Client(timeout=context.timeout_seconds, follow_redirects=False) as client:
                for i in range(burst_count):
                    resp = client.post(full_url, json={"email": f"test_rate_{i}@example.com", "password": "wrong"})
                    status_codes.append(resp.status_code)

                    headers = {k.lower(): v for k, v in resp.headers.items()}
                    if any(h in headers for h in ["retry-after", "x-ratelimit-limit", "x-ratelimit-remaining"]):
                        has_rate_limit_headers = True

                    # If server returns HTTP 429 Too Many Requests, rate limit is working properly!
                    if resp.status_code == 429:
                        break

            # If 100% of burst requests succeeded with 401 without receiving HTTP 429 or rate limit headers:
            if 429 not in status_codes and not has_rate_limit_headers and len(status_codes) >= burst_count:
                results.append(ScannerResult(
                    rule_id="SEC-RATE-01",
                    title="Unrestricted Rate Limiting on Authentication Endpoint",
                    severity="HIGH",
                    confidence="HIGH",
                    endpoint=auth_endpoint,
                    http_method="POST",
                    description=f"Endpoint accepted {len(status_codes)} rapid requests in burst without returning HTTP 429 or rate limit headers.",
                    evidence=f"Burst Requests Sent: {len(status_codes)}\nStatus Codes Received: {set(status_codes)}\nRate Limit Headers Present: None",
                    impact="Permits automated brute-force attacks against user credentials and API resources.",
                    remediation="Deploy rate-limiting middleware (e.g. 5 attempts per minute max) returning HTTP 429 with Retry-After header."
                ))
        except Exception:
            pass

        return results
