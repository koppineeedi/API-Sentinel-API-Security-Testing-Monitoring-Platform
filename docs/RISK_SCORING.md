# API Sentinel - Transparent Risk Scoring Engine Specification

## 1. Risk Score Overview

API Sentinel calculates a transparent **API Security Score** ranging from **0.0 to 100.0**, where **100.0** represents a pristine posture with zero active vulnerabilities, and **0.0** indicates severe vulnerability exposure.

---

## 2. Mathematical Scoring Formula

$$\text{Security Score} = \max\left(0.0, \min\left(100.0, 100.0 - \text{Finding Penalties} - \text{Exposure Penalties} - \text{Anomaly Penalties}\right)\right)$$

### 2.1 Finding Penalties (Unresolved `OPEN` / `CONFIRMED` Findings Only)

Each active finding incurs a base penalty weighted by finding severity and confidence multiplier:

$$\text{Finding Penalty} = \text{Base Severity Penalty} \times \text{Confidence Multiplier}$$

#### Base Severity Penalties
- **CRITICAL**: -25.0 points
- **HIGH**: -15.0 points
- **MEDIUM**: -8.0 points
- **LOW**: -3.0 points
- **INFO**: -1.0 point

#### Confidence Multipliers
- **HIGH**: $1.0\times$
- **MEDIUM**: $0.7\times$
- **LOW**: $0.4\times$

*Note: Transitioning a finding to `RESOLVED` or `FALSE_POSITIVE` immediately restores score points.*

---

### 2.2 Exposure & Anomaly Penalties

- **Attack Surface Exposure**: -5.0 penalty if monitored endpoints $> 20$.
- **Traffic Anomaly Penalty**: -10.0 penalty if recent 4xx/5xx traffic anomalies exceed threshold ($>10$).

---

## 3. Score Status Classifications

| Score Range | Status Label | Operational Risk Level |
| --- | --- | --- |
| **90.0 – 100.0** | `PRISTINE` | Excellent posture, minimal exposure |
| **75.0 – 89.9** | `LOW_RISK` | Low exposure, minor security advisories |
| **50.0 – 74.9** | `MODERATE_RISK` | Moderate exposure, elevated vulnerabilities |
| **25.0 – 49.9** | `HIGH_RISK` | Vulnerable posture, action required |
| **0.0 – 24.9** | `CRITICAL_EXPOSURE` | Immediate critical vulnerability remediation required |
