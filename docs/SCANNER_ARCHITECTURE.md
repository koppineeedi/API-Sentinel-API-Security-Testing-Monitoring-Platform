# API Sentinel Security Scanner Architecture & Specification

## 1. Executive Summary

API Sentinel features a modular, safe, high-performance security scanner engine designed specifically for authorized security testing across staging environments, local microservices, and lab APIs.

The engine strictly supports two operational modes:
1. **PASSIVE**: Inspects OpenAPI schemas, security headers, JWT token structure, and technology disclosure without sending active attack payloads.
2. **ACTIVE_AUTHORIZED**: Executes controlled security validation tests against explicitly configured target URLs with authorization tokens.

---

## 2. Scanner Framework Architecture

```
                       +----------------------------------+
                       |   SecurityScanner Orchestrator   |
                       +----------------+-----------------+
                                        |
      +---------------------------------+---------------------------------+
      |                 |               |                |                |
      v                 v               v                v                v
+-----------+     +-----------+   +-----------+    +-----------+    +-----------+
| Header    |     | Info      |   | JWT       |    | Auth      |    | BOLA      |
| Scanner   |     | Disclosure|   | Scanner   |    | Scanner   |    | Scanner   |
+-----------+     +-----------+   +-----------+    +-----------+    +-----------+
```

### 2.1 Core Scanner Modules

| Module Name | Mode | OWASP Category | Key Rules Audited |
| --- | --- | --- | --- |
| **`HeaderScanner`** | Passive | Security Misconfiguration | `SEC-HEAD-01` (HSTS, CSP, X-Content-Type-Options, Referrer-Policy, Cache-Control) |
| **`InformationDisclosureScanner`** | Passive | Information Disclosure | `SEC-INFO-01` (Server / Powered-By headers), `SEC-INFO-02` (Stack trace leaks) |
| **`JWTScanner`** | Passive | Broken Authentication | `SEC-JWT-01` (Unsigned `alg: none`), `SEC-JWT-02` (Missing `exp`), `SEC-JWT-03` (Excessive TTL >30d), `SEC-JWT-04` (Sensitive claims) |
| **`AuthenticationScanner`** | Both | Broken Authentication | `SEC-AUTH-01` (Unauthenticated state endpoints), `SEC-AUTH-02` (Missing auth 200), `SEC-AUTH-03` (Malformed token handling) |
| **`AuthorizationScanner`** | Active | BOLA / IDOR | `SEC-BOLA-01` (Controlled Identity A vs Identity B object access comparison) |
| **`RateLimitScanner`** | Active | Resource Consumption | `SEC-RATE-01` (Controlled 5-10 request burst testing for HTTP 429 & Retry-After) |
| **`InputValidationScanner`** | Passive | Injection | `SEC-INJ-01` (Unvalidated path parameter schema constraints) |

---

## 3. SSRF Protection & Safety Controls

The platform implements multi-layered Server-Side Request Forgery (SSRF) protections in `app.security.ssrf`:

1. **Host & IP Range Validation**:
   - Resolves target hostnames via DNS and blocks private/loopback networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.169.254` AWS IMDS metadata IP).
   - Local addresses (`127.0.0.1` / `localhost`) are strictly blocked unless `allow_local=True` is explicitly specified for local lab testing.
2. **HTTP Client Hardening**:
   - `follow_redirects=False`: Disables HTTP redirect traversal.
   - `timeout=5.0`: Hard 5-second request timeout.
   - `max_bytes=2MB`: Maximum payload response size limit preventing memory exhaustion.

---

## 4. Safe JWT Analysis & Token Masking

To prevent secret leakage in server logs and UI views, all JWT tokens are processed through `JWTScanner.mask_token()`:
- Header and signature bytes are sanitized (e.g. `eyJhbGci...eyJzdWIi...[MASKED_SIG]`).
- Secret key brute-forcing and password spraying are strictly prohibited by system design.
