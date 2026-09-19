import re
import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.project import APIProject
from app.models.endpoint import APIEndpoint
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.report import Report
from app.risk.engine import RiskEngine

class ReportGenerator:
    """
    Generates security assessment reports in HTML and PDF formats.
    Redacts sensitive secrets, passwords, complete JWT signatures, and private keys.
    """

    @staticmethod
    def sanitize_secrets(text: str) -> str:
        if not text:
            return ""
        # Redact JWT tokens
        text = re.sub(r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+', '[REDACTED_JWT_TOKEN]', text)
        # Redact private keys
        text = re.sub(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----', '[REDACTED_PRIVATE_KEY]', text)
        # Redact password fields in JSON/str
        text = re.sub(r'"password"\s*:\s*"[^"]+"', '"password": "[REDACTED_PASSWORD]"', text, flags=re.IGNORECASE)
        text = re.sub(r'password=[^\s&]+', 'password=[REDACTED_PASSWORD]', text, flags=re.IGNORECASE)
        text = re.sub(r'"api_key"\s*:\s*"[^"]+"', '"api_key": "[REDACTED_API_KEY]"', text, flags=re.IGNORECASE)
        text = re.sub(r'Bearer\s+[A-Za-z0-9-_.]+', 'Bearer [REDACTED_TOKEN]', text)
        return text

    @classmethod
    def generate_html_report(cls, db: Session, project: APIProject, report_title: str) -> str:
        endpoints = db.query(APIEndpoint).filter(APIEndpoint.project_id == project.id).all()
        findings = db.query(Finding).filter(Finding.project_id == project.id).all()
        last_scan = db.query(Scan).filter(Scan.project_id == project.id).order_by(Scan.created_at.desc()).first()

        # Dynamic risk score calculation
        score_details = RiskEngine.calculate_project_risk_score(db, project.id)
        security_score = score_details["overall_score"]
        status_label = score_details["status_label"]

        critical_f = [f for f in findings if f.severity.value == "CRITICAL"]
        high_f = [f for f in findings if f.severity.value == "HIGH"]
        med_f = [f for f in findings if f.severity.value == "MEDIUM"]
        low_f = [f for f in findings if f.severity.value == "LOW"]
        info_f = [f for f in findings if f.severity.value == "INFO"]

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{cls.sanitize_secrets(report_title)} - Security Assessment Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #0f172a; color: #f8fafc; line-height: 1.6; }}
        h1, h2, h3, h4 {{ color: #38bdf8; font-weight: 700; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
        .header {{ background-color: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #334155; }}
        .score-box {{ font-size: 32px; font-weight: bold; color: #38bdf8; margin: 15px 0; }}
        .badge {{ padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; display: inline-block; }}
        .critical {{ background: #7f1d1d; color: #fca5a5; }}
        .high {{ background: #7c2d12; color: #fdba74; }}
        .medium {{ background: #713f12; color: #fde047; }}
        .low {{ background: #14532d; color: #86efac; }}
        .info {{ background: #164e63; color: #67e8f9; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #1e293b; color: #94a3b8; font-family: monospace; }}
        pre {{ background-color: #020617; padding: 14px; border-radius: 8px; border: 1px solid #1e293b; overflow-x: auto; color: #38bdf8; font-size: 12px; }}
        .section {{ margin-bottom: 35px; background: #1e293b/40; padding: 20px; border-radius: 8px; border: 1px solid #334155; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>API Security Assessment Report</h1>
        <p><strong>Project Target:</strong> {cls.sanitize_secrets(project.name)} ({cls.sanitize_secrets(project.target_url)})</p>
        <p><strong>Generation Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <div class="score-box">API Security Score: {security_score:.1f} / 100 ({status_label})</div>
    </div>

    <!-- 1. Executive Summary -->
    <div class="section">
        <h2>1. Executive Summary</h2>
        <p>This security assessment report summarizes the security posture, vulnerability findings, and threat exposure for <strong>{cls.sanitize_secrets(project.name)}</strong>. The target API was evaluated using passive specification analysis and authorized active scanner modules.</p>
    </div>

    <!-- 2. Assessment Scope -->
    <div class="section">
        <h2>2. Assessment Scope</h2>
        <p>Base Target URL: <code>{cls.sanitize_secrets(project.target_url)}</code></p>
        <p>Total Cataloged Endpoints: {len(endpoints)}</p>
    </div>

    <!-- 3. API Inventory -->
    <div class="section">
        <h2>3. API Inventory</h2>
        <table>
            <thead>
                <tr>
                    <th>Method</th>
                    <th>Endpoint Path</th>
                    <th>Auth Standard</th>
                </tr>
            </thead>
            <tbody>
"""
        for ep in endpoints:
            html += f"<tr><td><strong>{ep.method}</strong></td><td><code>{cls.sanitize_secrets(ep.path)}</code></td><td>{cls.sanitize_secrets(ep.auth_type or 'None')}</td></tr>\n"

        html += f"""
            </tbody>
        </table>
    </div>

    <!-- 4. Security Score -->
    <div class="section">
        <h2>4. Security Score Breakdown</h2>
        <p>The transparent risk score is computed from active findings, missing security controls, and anomaly signals.</p>
        <p>Current Score: <strong>{security_score:.1f} / 100 ({status_label})</strong></p>
    </div>

    <!-- 5. Findings Summary -->
    <div class="section">
        <h2>5. Findings Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Severity Level</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
                <tr><td><span class="badge critical">CRITICAL</span></td><td>{len(critical_f)}</td></tr>
                <tr><td><span class="badge high">HIGH</span></td><td>{len(high_f)}</td></tr>
                <tr><td><span class="badge medium">MEDIUM</span></td><td>{len(med_f)}</td></tr>
                <tr><td><span class="badge low">LOW</span></td><td>{len(low_f)}</td></tr>
                <tr><td><span class="badge info">INFO</span></td><td>{len(info_f)}</td></tr>
            </tbody>
        </table>
    </div>

    <!-- Detailed Findings Section -->
    <div class="section">
        <h2>6. Detailed Findings & Evidence</h2>
"""
        for f in findings:
            clean_evidence = cls.sanitize_secrets(f.evidence or "")
            clean_impact = cls.sanitize_secrets(f.impact or "")
            clean_remediation = cls.sanitize_secrets(f.remediation or "")
            clean_desc = cls.sanitize_secrets(f.description or "")

            html += f"""
        <div style="margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px dashed #334155;">
            <h3>[{f.rule_id or 'SEC-RULE'}] {cls.sanitize_secrets(f.title)}</h3>
            <p><span class="badge {f.severity.value.lower()}">{f.severity.value}</span> | Status: <strong>{f.status.value}</strong> | Confidence: {f.confidence.value}</p>
            <p><strong>Description:</strong> {clean_desc}</p>
            <p><strong>Threat Impact:</strong> {clean_impact}</p>
            <p><strong>Remediation:</strong> {clean_remediation}</p>
            <h4>Observed Evidence:</h4>
            <pre>{clean_evidence}</pre>
        </div>
"""

        html += f"""
    </div>

    <!-- 15. Scan Information & 16. Methodology -->
    <div class="section">
        <h2>15. Scan Information & 16. Methodology</h2>
        <p><strong>Last Scan ID:</strong> {last_scan.id if last_scan else 'N/A'}</p>
        <p><strong>Scan Strategy Profile:</strong> {last_scan.scan_type if last_scan else 'PASSIVE'}</p>
        <p><strong>Methodology:</strong> Automated testing strictly adhering to OWASP API Security Top 10 guidelines for authorized security monitoring.</p>
    </div>
</body>
</html>
"""
        return html
