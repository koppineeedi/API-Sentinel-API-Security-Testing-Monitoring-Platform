import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.finding import Finding, FindingEvidence
from app.models.enums import FindingSeverity, FindingStatus, FindingConfidence
from app.models.project import APIProject
from app.models.endpoint import APIEndpoint
from app.detection.categories import RuleCategory

logger = logging.getLogger("APISentinelDetectionEngine")

class DetectionEngine:
    """
    Centralized Detection Engine.
    Consumes scanner outputs, traffic anomaly events, auth logs, and rate-limit observations,
    normalizing all security signals into structured findings in PostgreSQL.
    """

    @staticmethod
    def normalize_and_ingest_finding(
        db: Session,
        project_id: int,
        title: str,
        category: RuleCategory,
        severity: FindingSeverity,
        confidence: FindingConfidence,
        description: str,
        rule_id: Optional[str] = None,
        endpoint_id: Optional[int] = None,
        evidence: Optional[str] = None,
        impact: Optional[str] = None,
        remediation: Optional[str] = None
    ) -> Finding:
        # Check if identical open finding already exists to avoid duplication
        existing = db.query(Finding).filter(
            Finding.project_id == project_id,
            Finding.title == title,
            Finding.status == FindingStatus.OPEN
        ).first()

        if existing:
            if evidence and existing.evidence != evidence:
                existing.evidence = (existing.evidence or "") + f"\n\n[Additional Observation]\n{evidence}"
                db.commit()
            return existing

        new_finding = Finding(
            project_id=project_id,
            endpoint_id=endpoint_id,
            rule_id=rule_id or "SEC-DET-01",
            title=title,
            description=description,
            severity=severity,
            confidence=confidence,
            status=FindingStatus.OPEN,
            evidence=evidence,
            impact=impact or f"Potential security vulnerability under {category.value} category.",
            remediation=remediation or "Inspect application logic and enforce defensive validation controls."
        )
        db.add(new_finding)
        db.flush()

        if evidence:
            fe = FindingEvidence(
                finding_id=new_finding.id,
                payload=evidence,
                request_data={"category": category.value},
                response_data=None
            )
            db.add(fe)

        db.commit()
        db.refresh(new_finding)
        logger.info(f"[DetectionEngine] Ingested new finding ID #{new_finding.id}: '{title}' ({severity.value})")
        return new_finding
