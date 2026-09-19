# API Sentinel — API Security Testing & Monitoring Platform

> **Discover. Detect. Defend. — Intelligent API Security.**

API Sentinel is an authorized API security platform designed for security engineers, developers, and SecOps teams to continuously discover, audit, monitor, and analyze RESTful APIs against security risks, including the **OWASP API Security Top 10 (2023)**.

---

## Technical Highlights & Security Subsystems

- **OpenAPI 2.0/3.x Inventory & SSRF Protection**: Upload JSON/YAML specifications or import via URL with automated `SSRFProtector` private IP address restriction (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.169.254`).
- **Modular Active/Passive Scanner Engine**: Executes OWASP Top 10 scans across 7 specialized scanner modules (Header, Info Disclosure, JWT Analysis, Authentication, BOLA/Authorization, Rate Limiting, Input Validation).
- **Rule-Based Detection Engine**: Centralized normalization and automatic finding deduplication across 8 threat categories (`AUTHENTICATION`, `AUTHORIZATION`, `INPUT_VALIDATION`, `CONFIGURATION`, `CRYPTOGRAPHY`, `RATE_LIMITING`, `INFORMATION_DISCLOSURE`, `ANOMALY`).
- **Explainable Anomaly Engine**: Analyzes traffic telemetry to flag latency spikes ($\ge 3000\text{ms}$), HTTP 5xx errors, brute-force auth rejections (3+ 401/403s), burst traffic, and sensitive endpoint probing (`/admin`, `/.git`).
- **Transparent Risk Scoring (0–100 Score)**: Dynamic mathematical risk scoring weighted by finding severity, confidence multiplier, missing controls, and anomaly frequency.
- **AI Security Analyst (`AIProvider`)**: Structured context synthesis providing distinct `OBSERVED EVIDENCE`, `DETECTION RESULT`, `AI INTERPRETATION`, and `AI RECOMMENDATION` with offline mock fallback.
- **Asynchronous Scan Orchestration**: Non-blocking background scan execution supporting status tracking (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`) and live progress polling.
- **Security Assessment Reports**: One-click generation of professional HTML and PDF compliance reports with automated secret redaction (`sanitize_secrets`).
- **Immutable Security Audit Log**: Complete tracking of administrative logins, scan jobs, finding status lifecycle changes, report exports, and AI analysis events.

---

## Tech Stack

| Component | Technology / Library |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, React Router v6, Axios, Recharts, Lucide React |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, PostgreSQL (SQLite Fallback) |
| **Security & Auth** | PyJWT, Direct Bcrypt, Custom SSRFProtector |
| **Orchestration** | Docker, Docker Compose, BackgroundTasks, WebSocket (WSS) |
| **CI/CD** | GitHub Actions Workflow (`ci.yml`) |

---

## Project Architecture

```
API Sentinel Architecture
├── frontend/                     # React 18 SPA (Vite + Tailwind CSS + Recharts)
│   ├── src/pages/                # Dashboard, Inventory, Findings, Scans, Traffic, Reports, Audit
│   └── src/services/             # Axios API client & WebSocket handler
├── backend/app/                  # FastAPI Core Gateway
│   ├── detection/                # Centralized Detection Engine & Anomaly Engine
│   ├── models/                   # SQLAlchemy ORM Models (User, Project, Endpoint, Finding, Scan, Traffic, Audit)
│   ├── risk/                     # Transparent Risk Scoring Engine (0-100 API Score)
│   ├── routers/                  # RESTful API Endpoints
│   ├── security/                 # JWT Auth, Bcrypt, RBAC, SSRFProtector
│   └── services/                 # OpenAPI Parser, ReportGenerator, AIProvider
├── scanner/                      # Modular Active/Passive OWASP Scanner Framework
│   ├── base.py                   # ScannerContext & BaseScanner
│   ├── modules/                  # Specialized Scanner Modules (BOLA, JWT, Headers, Rate Limit, Input)
│   └── orchestrator.py           # SecurityScanner Engine
├── tests/                        # Pytest Test Suite (35/35 Unit & Integration Tests)
├── docker-compose.yml            # Container Orchestration
└── README.md                     # Documentation
```

---

## Quick Start & Installation

### Local Setup (Development Mode)

1. **Clone Repository**:
   ```bash
   git clone https://github.com/organization/api-sentinel.git
   cd api-sentinel
   ```

2. **Backend Setup**:
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Linux/macOS: source venv/bin/activate

   pip install -r backend/requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:5173` in your browser. Default Admin Credentials: `admin@sentinel.com` / `AdminPass123!`.

---

## Docker Deployment

To launch the complete platform (PostgreSQL + FastAPI Gateway + React Frontend + Worker Scanner) via Docker Compose:

```bash
docker-compose up --build -d
```

Check health:
```bash
docker-compose ps
```

---

## Automated Test Verification

Run the backend test suite:

```bash
python -m pytest tests -v
```

Expected result:
```
====================== 35 passed in 21.38s ======================
```

---

## Authorized Testing Policy

API Sentinel is strictly intended for **authorized security testing** on local applications, staging environments, laboratory setups, and target systems where explicit permission is granted. **Do not use this software against unauthorized targets.**

---

## Implementation Status & Limitations

- **Core Implementation**: Complete.
- **Docker Validation Note**: Docker Compose configuration is defined in `docker-compose.yml`. Execution in local dev environment uses standalone Uvicorn + Vite stack (Docker CLI not installed on host PATH).
- **Background Scans**: Executes via FastAPI `BackgroundTasks`. Distributed Celery queues planned for future cloud scaling.
