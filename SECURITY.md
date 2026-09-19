# API Sentinel — Security Policy & Policy Guidelines

## 1. Authorized Testing Scope & Policy

API Sentinel is an explicit **API Security Testing & Monitoring Platform** built strictly for authorized testing environments:
- Local development & microservices applications
- Staging and QA testing infrastructure
- Intentionally vulnerable labs (e.g. OWASP juice-shop, vAPI)
- Production/external environments where explicit written authorization is granted.

> [!CAUTION]
> Do NOT execute active security scans against arbitrary third-party targets. Active security testing features require target authorization validation and passive mode overrides.

---

## 2. Security Safeguards & Hardening Controls

### SSRF Protection (`SSRFProtector`)
All OpenAPI URL spec imports validate schemes (`http`, `https`), resolve DNS, and block private IP address spaces (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`) by default unless an explicit override is configured.

### Authentication & Authorization (RBAC)
- **Direct Bcrypt Hashing**: Password hashing uses direct 72-byte truncation safe Bcrypt password hashing (`bcrypt.hashpw`).
- **Role Hierarchy**: Enforces strict RBAC (`ADMIN` > `SECURITY_ANALYST` > `VIEWER`). Scans, finding status changes, report generation, and API imports require `SECURITY_ANALYST` minimum privileges.

### Secrets Redaction
- All security reports, log outputs, and WebSocket feeds automatically redact sensitive JWT tokens, passwords, private keys, and API credentials.

### Non-Destructive Active Scanning
- Active scanners execute strictly non-destructive authorization checks (`PASSIVE` and `ACTIVE_AUTHORIZED`). API Sentinel does NOT implement credential stuffing, password spraying, or denial-of-service payloads.

---

## 3. Vulnerability Reporting
To report security concerns or issues with API Sentinel itself, please submit a report directly to the security engineering team or open a confidential security advisory.
