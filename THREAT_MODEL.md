# API Sentinel — Threat Model & Security Architecture

## 1. System Overview & Trust Boundaries

```
                       [ User / Browser ]
                                |
                        (HTTPS / WSS + JWT)
                                |
                                v
                     +--------------------+
                     |  FastAPI Gateway   |
                     +--------------------+
                        /        |       \
                       /         |        \
                      v          v         v
             [Detection Engine] [Risk] [Traffic WS]
                      |          |
                      v          v
              [SQLAlchemy / PostgreSQL DB]
```

### Key Trust Boundaries:
1. **Client / Browser <-> FastAPI Gateway**: Untrusted input boundary. Protected by JWT Bearer tokens, CORS policies, Pydantic input schemas.
2. **FastAPI <-> Remote OpenAPI URLs**: High-risk SSRF boundary. Protected by `SSRFProtector` DNS/IP filtering.
3. **FastAPI <-> Target APIs**: Authorized active scanner boundary. Enforces non-destructive authorized target URLs.

---

## 2. Threat Matrix (STRIDE Analysis)

| Threat Category | Threat Description | Attack Vector | Mitigation in API Sentinel |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker impersonates Security Analyst or Admin | Invalid JWT tokens | PyJWT signature verification with configurable `JWT_SECRET_KEY` and short token lifetimes. |
| **Tampering** | Parameter tampering or SQL Injection | Malicious API payloads | SQLAlchemy ORM parameterized queries and strict Pydantic validation. |
| **Repudiation** | User denies performing finding status change or scan launch | Unlogged admin actions | Centralized audit logger (`AuditLog`) recording timestamp, user ID, resource ID, and action. |
| **Information Disclosure** | Leakage of credentials or sensitive data in reports/traffic logs | Unredacted request bodies | Automatic regex secret redaction (`sanitize_secrets`) and body payload masking. |
| **Denial of Service** | Resource exhaustion via excessive scan requests | Background scan loop abuse | Cooperative cancellation, background worker thread pools, and max burst limits. |
| **Elevation of Privilege** | `VIEWER` role triggers scans or alters finding status | Privilege escalation | RBAC dependency checks (`require_minimum_role`) enforced on FastAPI routes. |
| **SSRF** | URL-based spec import targets internal cloud metadata (169.254.169.254) | Malicious spec URL import | `SSRFProtector` URL & private IP address filter. |

---

## 3. Residual Risk & Recommendations

1. Ensure production deployments run over HTTPS/TLS with secure HTTP-only cookies or authorization header tokens.
2. Store production secrets (e.g. `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`) in secret management vaults, never in plaintext repository files.
