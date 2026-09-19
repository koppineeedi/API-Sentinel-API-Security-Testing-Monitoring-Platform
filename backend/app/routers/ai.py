from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.finding import Finding
from app.models.ai import AIAnalysis
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.ai import AIAnalysisCreate, AIAnalysisResponse
from app.security.rbac import require_minimum_role
from app.services.ai_provider import get_ai_provider
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/ai", tags=["AI Analysis"])

@router.post("/analyze", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_finding_with_ai(
    analysis_in: AIAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    finding = db.query(Finding).filter(Finding.id == analysis_in.finding_id).first()
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    existing_analysis = db.query(AIAnalysis).filter(AIAnalysis.finding_id == finding.id).first()
    if existing_analysis:
        return existing_analysis

    provider = get_ai_provider()
    finding_data = {
        "id": finding.id,
        "title": finding.title,
        "description": finding.description,
        "severity": finding.severity.value,
        "confidence": finding.confidence.value,
        "evidence": finding.evidence,
        "rule_id": finding.rule_id
    }

    ai_res = provider.analyze_finding(finding_data)

    analysis = AIAnalysis(
        finding_id=finding.id,
        summary=ai_res["summary"],
        root_cause=ai_res["root_cause"],
        custom_remediation=ai_res["custom_remediation"],
        risk_score=ai_res["risk_score"],
        model_used=ai_res["model_used"]
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="AI_ANALYSIS_PERFORMED",
        resource_type="Finding",
        resource_id=str(finding.id),
        details={"model_used": analysis.model_used, "risk_score": analysis.risk_score}
    )

    return analysis
