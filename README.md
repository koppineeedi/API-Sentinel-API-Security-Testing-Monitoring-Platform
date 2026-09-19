# API Sentinel — API Security Testing & Monitoring Platform

> **Discover. Detect. Defend. — Intelligent API Security.**

API Sentinel is a production-grade **API Security Testing & Monitoring Platform** designed for security engineers, developers, and SecOps teams to continuously discover, audit, monitor, and analyze RESTful APIs against security vulnerabilities, including the **OWASP API Security Top 10 (2023)**.

---

## 📌 Executive Overview: From Scratch to End

API Sentinel provides an end-to-end security lifecycle for target API applications. Instead of relying on isolated point tools, API Sentinel unifies spec discovery, non-destructive vulnerability scanning, rule-based threat normalization, telemetry anomaly monitoring, dynamic risk scoring, AI-assisted risk synthesis, and compliance report generation into a single SecOps platform.

```
+-----------------------------------------------------------------------------------+
|                            API SENTINEL WORKFLOW PIPELINE                          |
+-----------------------------------------------------------------------------------+
| 1. API Discovery      --> Import OpenAPI JSON/YAML with SSRFProtector URL Check   |
| 2. Vulnerability Scan --> Execute Active/Passive Scanners across 7 OWASP Modules  |
| 3. Threat Engine      --> Normalize & Deduplicate Findings across 8 Categories   |
| 4. Telemetry Monitor  --> Capture HTTP Traffic, Flag Anomalies & Latency Spikes   |
| 5. Risk Scoring       --> Compute 0-100 Transparent API Risk Score & Rating       |
| 6. Finding Lifecycle  --> Manage State Transitions (OPEN -> CONFIRMED -> RESOLVED)|
| 7. Compliance Report  --> Export Executive HTML/PDF Reports with Secret Redaction |
| 8. AI Synthesis       --> Structured AI Risk Analysis with Offline Fallback Mode  |
+-----------------------------------------------------------------------------------+
```

---

## ⚙️ Step-by-Step Operational Workflow

1. **Authentication & RBAC Setup**: Users register and authenticate via JWT bearer tokens. Roles (`ADMIN`, `SECURITY_ANALYST`, `VIEWER`) govern access across administrative endpoints.
2. **API Inventory & SSRF Protection**: Import OpenAPI 2.0/3.x specifications via JSON/YAML drag-and-drop or explicit URL fetching. Remote spec requests are validated by `SSRFProtector` to block loopback (`127.0.0.1`), private RFC 1918 networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and AWS cloud metadata IP (`169.254.169.254`).
3. **Vulnerability Scanning**: Security analysts configure scan jobs (`FULL`, `PASSIVE`, `BOLA_ONLY`, `AUTH_ONLY`, `INPUT_VALIDATION`). The scanner orchestrator executes non-destructive active/passive probes in the background without blocking API request threads.
4. **Normalized Detection**: Security findings are normalized into standard formats, categorized into 8 threat categories (`AUTHENTICATION`, `AUTHORIZATION`, `INPUT_VALIDATION`, `CONFIGURATION`, `CRYPTOGRAPHY`, `RATE_LIMITING`, `INFORMATION_DISCLOSURE`, `ANOMALY`), and automatically deduplicated.
5. **Traffic Anomaly Monitoring**: Authorized API traffic metadata (method, route, status, latency, IP) is recorded in real time. The explainable `AnomalyEngine` flags latency spikes ($\ge 3000\text{ms}$), HTTP 5xx errors, brute-force auth rejections (3+ 401/403s), burst volume, and sensitive route probing (`/admin`, `/.git`).
6. **Transparent Risk Engine**: Computes a dynamic 0.0 to 100.0 API Security Score based on weighted finding severities, confidence multipliers, missing security controls, and anomaly frequencies:
   $$\text{Score} = \max\left(0.0, 100.0 - \text{Finding Penalties} - \text{Exposure Penalties} - \text{Anomaly Penalties}\right)$$
7. **Finding State Machine & Audit Trail**: Analysts inspect technical request/response evidence and transition statuses (`OPEN` $\rightarrow$ `CONFIRMED` $\rightarrow$ `RESOLVED` / `FALSE_POSITIVE`). Every status change generates an immutable audit log record.
8. **Compliance Reporting**: Generate 16-section HTML or PDF assessment reports. Regex sanitization (`sanitize_secrets`) automatically redacts passwords, private keys, complete JWT signatures, and API keys.
9. **AI Security Analyst Synthesis**: Structured AI analysis (`AIProvider`) generates clear breakdowns: `OBSERVED EVIDENCE`, `DETECTION RESULT`, `AI INTERPRETATION`, and `AI RECOMMENDATION` with clean offline fallback when no LLM API key is configured.

---

## 🌟 Key Advantages & Engineering Benefits

### 1. Complete OWASP API Security Top 10 Coverage
Dedicated scanner modules test target APIs for BOLA/IDOR, Broken Authentication, Security Misconfigurations, Rate Limiting vulnerabilities, JWT algorithm confusion/unsigned tokens, Information Disclosure, and Parameter Injection.

### 2. Strict SSRF Protection for Remote Imports
Unlike naive HTTP spec fetching, `SSRFProtector` resolves hostnames to IP addresses before initiating requests, safeguarding internal enterprise infrastructure from server-side request forgery attacks.

### 3. Deterministic Detection & Transparent Scoring (No Black Boxes)
Finding detection and risk scoring are strictly deterministic. The engine provides mathematical penalty breakdowns and human-readable anomaly flag reasons rather than unexplainable scores.

### 4. Non-Destructive Authorized Scanning Boundary
Scanning modules enforce authorized target URL boundaries. API Sentinel does **not** implement destructive exploit payloads, credential stuffing, password spraying, or denial-of-service behaviors.

### 5. Automated Secret Redaction Across Reports & Logs
All HTML/PDF compliance exports, audit logs, and telemetry feeds automatically strip sensitive JWT signatures, authorization headers, private keys, and passwords.

### 6. Flexible AI Provider Architecture
`AIProvider` abstraction supports `MockAIProvider` (offline local fallback), `OpenAIProvider`, and `AnthropicProvider`. Provider credentials remain strictly server-side and are never exposed to the frontend.

---

## ⚠️ Disadvantages & Technical Limitations (Tradeoffs)

### 1. Single-Host Background Scan Execution
- **Limitation**: Background scans execute asynchronously using FastAPI `BackgroundTasks` in the gateway process.
- **Tradeoff**: Ideal for local development, staging environments, and single-tenant labs. Distributed worker queues (e.g. Celery + Redis) would be required for high-scale multi-tenant enterprise scanning.

### 2. Host Environment Dependency for Container Runtimes
- **Limitation**: Containerized multi-service execution via `docker-compose.yml` relies on Docker Engine / Docker Desktop being installed on the host.
- **Tradeoff**: On host systems without Docker installed, the application falls back seamlessly to the standalone Uvicorn + Vite stack with SQLite local storage.

### 3. Manual / Static OpenAPI Specification Import
- **Limitation**: Endpoint inventory relies on OpenAPI JSON/YAML spec uploads or valid URL spec endpoints.
- **Tradeoff**: Dynamic specification reconstruction directly from un-documented live HTTP traffic streams is planned for future platform iterations.

---

## 🛠️ Technology Stack

| Layer | Technology / Framework |
| :--- | :--- |
| **Frontend SPA** | React 18, Vite, Tailwind CSS, React Router v6, Axios, Recharts, Lucide React |
| **Backend API Gateway** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, PostgreSQL (SQLite Fallback) |
| **Security Subsystems** | PyJWT, Direct Bcrypt, Custom SSRFProtector |
| **Orchestration & Stream** | Docker, Docker Compose, BackgroundTasks, Real-Time WebSocket (WSS) |
| **CI/CD Pipeline** | GitHub Actions Workflow (`.github/workflows/ci.yml`) |

---

## 🚀 Quick Start & Installation

### Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/koppineeedi/API-Sentinel-API-Security-Testing-Monitoring-Platform.git
   cd API-Sentinel-API-Security-Testing-Monitoring-Platform
   ```

2. **Backend Setup**:
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/macOS: source venv/bin/activate

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

## 🐳 Docker Deployment

To launch the complete containerized stack (PostgreSQL + FastAPI Gateway + React Frontend + Worker Scanner) via Docker Compose:

```bash
docker-compose up --build -d
```

Check container status:
```bash
docker-compose ps
```

---

## 🧪 Automated Test Verification

Run the backend pytest suite (35 unit & integration test cases):

```bash
python -m pytest tests -v
```

Expected output:
```
====================== 35 passed in 21.38s ======================
```

Verify frontend production build:
```bash
cd frontend && npm run build
```

---

## 🔒 Authorized Security Testing Policy

API Sentinel is strictly designed for **authorized security testing** on local applications, staging environments, laboratory setups, and target systems where explicit written scanning permission has been granted. **Do not use this software against unauthorized third-party targets.**
