# API Sentinel - System Architecture & Security Specification

## 1. System Overview

**API Sentinel** is an enterprise-grade API Security Testing & Monitoring Platform engineered specifically for authorized security testing across local environments, staging infrastructure, intentionally vulnerable labs, and production APIs with explicit scanning consent.

```
                  +-----------------------------------+
                  |      React SPA Frontend (Vite)    |
                  |     Tailwind CSS / Recharts       |
                  +-----------------+-----------------+
                                    |
                                    | REST API (JWT Auth) + WebSocket
                                    v
                  +-----------------+-----------------+
                  |      FastAPI Backend Gateway      |
                  |   CORS, Pydantic, RBAC Guard      |
                  +--------+----------------+---------+
                           |                |
           +---------------+                +---------------+
           |                                                |
           v                                                v
+----------+----------+                          +----------+----------+
|  PostgreSQL / DB    |                          |   Scanner Engine &  |
|  SQLAlchemy ORM     |                          |  Detection Rules    |
+---------------------+                          +---------------------+
```

---

## 2. Core Architectural Subsystems

### 2.1 Backend Gateway (`backend/app/`)
- **FastAPI Core**: Asynchronous API endpoints with strict Pydantic v2 validation.
- **ORM & Database**: SQLAlchemy 2.0 with PostgreSQL driver and SQLite fallback for local testing.
- **Authentication & Security**: JWT bearer authorization (`HS256`), bcrypt salted password hashing, stateful audit logging (`AuditLog`).
- **RBAC Matrix**: Enforces role hierarchy across endpoints (`ADMIN` > `SECURITY_ANALYST` > `VIEWER`).

### 2.2 Centralized Detection Engine & Anomaly Engine (`backend/app/detection/`)
- **Normalized Ingestion**: Normalizes scanner observations, authentication events, JWT claims, and rate limit observations into standard `Finding` records.
- **Rule Categories**: `AUTHENTICATION`, `AUTHORIZATION`, `INPUT_VALIDATION`, `CONFIGURATION`, `CRYPTOGRAPHY`, `RATE_LIMITING`, `INFORMATION_DISCLOSURE`, `ANOMALY`.
- **Explainable Anomaly Detection**: Evaluates latency spikes ($\ge 3000\text{ms}$), HTTP 5xx errors, brute-force auth rejections (3+ 401/403s), burst traffic, and sensitive endpoint probing (`/admin`, `/.git`).

### 2.3 Transparent Risk Engine (`backend/app/risk/`)
- Calculates a 0.0 to 100.0 API Security Score:
  $$\text{Score} = \max\left(0.0, 100.0 - \text{Finding Penalties} - \text{Exposure Penalties} - \text{Anomaly Penalties}\right)$$
- Risk Status Labels: `PRISTINE` (90–100), `LOW_RISK` (75–89.9), `MODERATE_RISK` (50–74.9), `HIGH_RISK` (25–49.9), `CRITICAL_EXPOSURE` (0–24.9).

### 2.4 AI Security Analyst (`backend/app/services/ai_provider.py`)
- **`AIProvider` Abstraction**: `MockAIProvider`, `OpenAIProvider`, `AnthropicProvider`.
- **Output Structure**: Explicit separation of `OBSERVED EVIDENCE`, `DETECTION RESULT`, `AI INTERPRETATION`, and `AI RECOMMENDATION`.
- Fallback: Gracefully operates offline when LLM API keys are unconfigured.

### 2.5 Security Assessment Report Service (`backend/app/services/report_service.py`)
- Generates 16-section executive compliance reports in HTML and PDF formats.
- Automatically redacts passwords, private keys, complete JWT signatures, and API tokens.

### 2.6 Background Scan Orchestrator (`backend/app/routers/scans.py` & `scanner/`)
- Executes asynchronous vulnerability scans using FastAPI `BackgroundTasks`.
- States: `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`.
- Cooperative cancellation polling and non-blocking job updates.

---

## 3. Frontend SPA (`frontend/`)

- **React 18 + Vite**: High-performance single page application built with Tailwind CSS, Lucide React, and Recharts.
- **Pages**:
  - `Dashboard`: Real-time risk score gauge, severity breakdown donut, HTTP status distribution, and active audit overview.
  - `API Inventory`: Project catalog, endpoint parameters, headers, and specification inspection drawer.
  - `Findings`: Filterable finding catalog, forensic request/response evidence viewer, AI analysis synthesis, state transition lifecycle (`OPEN`, `CONFIRMED`, `FALSE_POSITIVE`, `RESOLVED`).
  - `Scans`: Scan execution wizard, module strategy selector, live progress tracking, cancel scan trigger.
  - `Traffic Monitor`: HTTP transaction trace inspector, latency distribution, real-time WebSocket feed.
  - `Reports`: HTML & PDF report generator and download center.
  - `Audit Logs`: Administrative audit trails with search, filter, and user action tracking.
  - `Settings`: User security settings and API key management.
