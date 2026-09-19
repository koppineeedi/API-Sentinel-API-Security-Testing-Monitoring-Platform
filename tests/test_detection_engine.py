import pytest
from app.detection.engine import DetectionEngine
from app.detection.categories import RuleCategory
from app.models.enums import FindingSeverity, FindingConfidence, FindingStatus
from app.models.finding import Finding
from app.models.project import APIProject

def test_detection_engine_ingest_and_deduplication(db_session):
    # Create test project
    project = APIProject(name="Detection Lab", target_url="http://localhost:8000", created_by_id=1)
    db_session.add(project)
    db_session.commit()

    # 1. Ingest initial finding
    f1 = DetectionEngine.normalize_and_ingest_finding(
        db=db_session,
        project_id=project.id,
        title="Unauthenticated Admin Route Access",
        category=RuleCategory.AUTHENTICATION,
        severity=FindingSeverity.HIGH,
        confidence=FindingConfidence.HIGH,
        description="Endpoint /admin/config allows unauthenticated access",
        evidence="GET /admin/config -> HTTP 200 OK"
    )
    assert f1.id is not None
    assert f1.status == FindingStatus.OPEN

    # 2. Ingest identical finding (should append evidence rather than duplicate record)
    f2 = DetectionEngine.normalize_and_ingest_finding(
        db=db_session,
        project_id=project.id,
        title="Unauthenticated Admin Route Access",
        category=RuleCategory.AUTHENTICATION,
        severity=FindingSeverity.HIGH,
        confidence=FindingConfidence.HIGH,
        description="Endpoint /admin/config allows unauthenticated access",
        evidence="Second observation"
    )
    assert f1.id == f2.id
    assert "Second observation" in f1.evidence
