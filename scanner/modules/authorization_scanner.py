import httpx
from typing import List
from scanner.base import BaseScanner, ScannerContext, ScannerResult, ScannerMode

class AuthorizationScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "AuthorizationScanner"

    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        results: List[ScannerResult] = []

        # BOLA/IDOR testing REQUIRES ACTIVE_AUTHORIZED mode and explicit Identity A & B tokens
        if context.mode != ScannerMode.ACTIVE_AUTHORIZED:
            return results

        if not (context.auth_token_a and context.auth_token_b and context.bola_target_id):
            # Controlled BOLA testing requires explicit configuration
            return results

        target_url = context.target_url.rstrip("/")

        # Controlled BOLA test on target endpoint (e.g. /api/v1/users/{id})
        target_path = f"/api/v1/users/{context.bola_target_id}"
        full_url = f"{target_url}{target_path}"

        try:
            with httpx.Client(timeout=context.timeout_seconds, follow_redirects=False) as client:
                # Request 1: Identity A (Owner) fetches resource -> Expected HTTP 200
                res_a = client.get(full_url, headers={"Authorization": f"Bearer {context.auth_token_a}"})

                # Request 2: Identity B (Unauthorized User) attempts to fetch Identity A's resource -> Expected HTTP 403 or 404
                res_b = client.get(full_url, headers={"Authorization": f"Bearer {context.auth_token_b}"})

                # BOLA Vulnerability Condition: Identity B receives HTTP 200 OK accessing Identity A's object
                if res_a.status_code == 200 and res_b.status_code == 200:
                    results.append(ScannerResult(
                        rule_id="SEC-BOLA-01",
                        title=f"Broken Object Level Authorization (BOLA) on {target_path}",
                        severity="CRITICAL",
                        confidence="HIGH",
                        endpoint=target_path,
                        http_method="GET",
                        description="User Identity B successfully accessed private object data belonging to User Identity A without authorization error.",
                        evidence=(
                            f"Identity A GET {full_url} -> HTTP {res_a.status_code}\n"
                            f"Identity B GET {full_url} -> HTTP {res_b.status_code} (Unauthorized Access Granted)"
                        ),
                        impact="Allows attackers to access or mutate private data belonging to any user by modifying object identifiers in URLs.",
                        remediation="Implement object-level ownership checks in service layer verifying that session user owns the requested object ID."
                    ))
        except Exception:
            pass

        return results
