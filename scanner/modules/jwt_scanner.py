import json
import base64
import time
from typing import List, Dict, Any, Optional
from scanner.base import BaseScanner, ScannerContext, ScannerResult

class JWTScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "JWTScanner"

    @staticmethod
    def mask_token(token: str) -> str:
        """
        Safely masks JWT signature and sensitive payload bytes for logs and UI reporting.
        """
        if not token or not isinstance(token, str):
            return "N/A"
        parts = token.split(".")
        if len(parts) != 3:
            return token[:6] + "...[MASKED]"
        return f"{parts[0][:8]}...{parts[1][:8]}...[MASKED_SIG]"

    @staticmethod
    def decode_token_unverified(token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            # Add padding
            payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
            header_b64 = parts[0] + "=" * (-len(parts[0]) % 4)
            
            header = json.loads(base64.urlsafe_b64decode(header_b64).decode('utf-8'))
            payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
            return {"header": header, "payload": payload}
        except Exception:
            return None

    def scan(self, context: ScannerContext) -> List[ScannerResult]:
        results: List[ScannerResult] = []
        tokens_to_test = []
        if context.auth_token_a:
            tokens_to_test.append(("Token A", context.auth_token_a))
        if context.auth_token_b:
            tokens_to_test.append(("Token B", context.auth_token_b))

        for token_label, raw_token in tokens_to_test:
            decoded = self.decode_token_unverified(raw_token)
            masked = self.mask_token(raw_token)

            if not decoded:
                continue

            header = decoded.get("header", {})
            payload = decoded.get("payload", {})

            # 1. Check for insecure algorithm "none"
            alg = str(header.get("alg", "")).lower()
            if alg == "none":
                results.append(ScannerResult(
                    rule_id="SEC-JWT-01",
                    title="Insecure JWT Unsigned Algorithm ('alg: none')",
                    severity="CRITICAL",
                    confidence="HIGH",
                    endpoint="JWT Configuration",
                    http_method="AUTH",
                    description=f"JWT token uses algorithm 'none', allowing arbitrary unsigned token forgery.",
                    evidence=f"Masked Token: {masked}\nDecoded Header: {header}",
                    impact="Attain complete authentication bypass and privilege escalation across all protected endpoints.",
                    remediation="Configure JWT verifier to strictly require RS256 or HS256 signatures and reject 'none' algorithm."
                ))

            # 2. Check for missing expiration ('exp')
            exp = payload.get("exp")
            if not exp:
                results.append(ScannerResult(
                    rule_id="SEC-JWT-02",
                    title="Missing Expiration Claim ('exp') in JWT",
                    severity="HIGH",
                    confidence="HIGH",
                    endpoint="JWT Token Policy",
                    http_method="AUTH",
                    description="Authentication token lacks an expiration timestamp, remaining valid indefinitely.",
                    evidence=f"Masked Token: {masked}\nDecoded Payload Claims: {list(payload.keys())}",
                    impact="Stolen session tokens remain permanently valid without expiration limits.",
                    remediation="Include explicit 'exp' expiration timestamps in all issued JWT tokens."
                ))
            else:
                # 3. Check for excessive expiration (> 30 days)
                now = time.time()
                ttl_seconds = exp - now
                if ttl_seconds > 2592000: # 30 days
                    results.append(ScannerResult(
                        rule_id="SEC-JWT-03",
                        title="Excessive Token Validity Duration (>30 Days)",
                        severity="MEDIUM",
                        confidence="HIGH",
                        endpoint="JWT Token Policy",
                        http_method="AUTH",
                        description=f"JWT expiration is set far in the future (~{int(ttl_seconds / 86400)} days).",
                        evidence=f"Masked Token: {masked}\nExpiration (exp): {exp} (TTL: {int(ttl_seconds / 86400)} days)",
                        impact="Extended exposure window for compromised tokens.",
                        remediation="Reduce access token TTL (recommended 15m to 8h) and utilize refresh tokens for session renewal."
                    ))

            # 4. Check for suspicious claims (e.g. sensitive password/secret in payload)
            sensitive_keys = ["password", "secret", "private_key", "ssn", "credit_card"]
            found_keys = [k for k in payload.keys() if any(sk in k.lower() for sk in sensitive_keys)]
            if found_keys:
                results.append(ScannerResult(
                    rule_id="SEC-JWT-04",
                    title="Sensitive Information Disclosed in JWT Payload",
                    severity="HIGH",
                    confidence="HIGH",
                    endpoint="JWT Token Payload",
                    http_method="AUTH",
                    description=f"JWT payload contains sensitive data fields: {', '.join(found_keys)}.",
                    evidence=f"Masked Token: {masked}\nSensitive Keys Disclosed: {found_keys}",
                    impact="JWT payloads are base64-encoded and readable by any client or proxy.",
                    remediation="Remove sensitive credentials from JWT claims; store user identifiers only."
                ))

        return results
