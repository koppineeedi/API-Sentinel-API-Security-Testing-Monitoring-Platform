# API Sentinel Centralized Detection & Anomaly Engine

## 1. Architecture Overview

The Centralized Detection Engine in API Sentinel normalizes security signals from multi-vector observers (Security Scanner, API Traffic Monitor, Authentication Logger, and Anomaly Evaluator) into standardized `Finding` records.

```
+-------------------+      +-------------------+      +-------------------+
| Security Scanner  |      | Traffic Ingestion |      |  Auth & JWT Logs  |
+---------+---------+      +---------+---------+      +---------+---------+
          |                          |                          |
          +--------------------------+--------------------------+
                                     |
                                     v
                        +------------+------------+
                        |     DetectionEngine     |
                        | (Rule Normalization)    |
                        +------------+------------+
                                     |
                                     v
                        +------------+------------+
                        |   PostgreSQL Findings   |
                        +-------------------------+
```

---

## 2. Rule Categories

Security findings are classified into 8 core categories:

1. **`AUTHENTICATION`**: Token verification failures, unauthenticated state-changing routes, missing auth headers.
2. **`AUTHORIZATION`**: Broken Object Level Authorization (BOLA / IDOR) and privilege escalation vectors.
3. **`INPUT_VALIDATION`**: Unvalidated path parameters, missing type/format constraints, and injection risks.
4. **`CONFIGURATION`**: Security misconfigurations and missing defensive HTTP headers.
5. **`CRYPTOGRAPHY`**: Insecure JWT algorithms (`alg: none`), weak secrets, and transport security flaws.
6. **`RATE_LIMITING`**: Missing rate limit controls on authentication and sensitive computational endpoints.
7. **`INFORMATION_DISCLOSURE`**: Server version disclosure headers, verbose error messages, and stack trace leaks.
8. **`ANOMALY`**: Real-time traffic anomaly signals and behavioral deviation flags.

---

## 3. Explainable Anomaly Detection Engine

The Anomaly Engine (`app.detection.anomaly_engine`) evaluates live API transactions against 5 transparent, explainable signals:

1. **Latency Spike**: Response latency $\ge 3000\text{ms}$ (+0.35 score).
2. **Server Error Exception**: HTTP 5xx responses (+0.30 score).
3. **Repeated Authentication Failures**: 3+ HTTP 401/403 security rejections from single IP (+0.45 score).
4. **Abnormal Request Volume**: Burst volume exceeding baseline limit (+0.40 score).
5. **Sensitive Endpoint Probe**: Unauthorized requests targeting `/admin`, `/config`, or `/.git` routes (+0.35 score).

Every anomaly decision attaches explicit human-readable `flag_reasons` to ensure full auditability.
