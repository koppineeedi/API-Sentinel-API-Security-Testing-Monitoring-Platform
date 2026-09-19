import pytest
from app.risk.engine import RiskEngine
from app.models.project import APIProject
from app.models.finding import Finding
from app.models.enums import FindingSeverity, FindingConfidence, FindingStatus

def test_risk_score_calculation(db_session):
    project = APIProject(name="Risk Test API", target_url="http://localhost:8000", created_by_id=1)
    db_session.add(project)
    db_session.commit()

    # Initial pristine score without active findings
    report1 = RiskEngine.calculate_project_risk_score(db_session, project.id)
    assert report1["overall_score"] == 100.0
    assert report1["status_label"] == "PRISTINE"

    # Add Critical Finding
    f_crit = Finding(
        project_id=project.id,
        title="BOLA Vulnerability",
        severity=FindingSeverity.CRITICAL,
        confidence=FindingConfidence.HIGH,
        status=FindingStatus.OPEN
    )
    db_session.add(f_crit)
    db_session.commit()

    report2 = RiskEngine.calculate_project_risk_score(db_session, project.id)
    assert report2["overall_score"] == 75.0 # 100 - 25
    assert report2["findings_by_severity"]["CRITICAL"] == 1

    # Resolve Critical Finding -> Score restored to 100
    f_crit.status = FindingStatus.RESOLVED
    db_session.commit()

    report3 = RiskEngine.calculate_project_risk_score(db_session, project.id)
    assert report3["overall_score"] == 100.0
