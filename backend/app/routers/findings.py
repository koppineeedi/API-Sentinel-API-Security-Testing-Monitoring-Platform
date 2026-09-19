from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.finding import Finding
from app.models.project import APIProject
from app.models.user import User
from app.models.enums import UserRole, FindingSeverity, FindingStatus, FindingConfidence
from app.schemas.finding import FindingCreate, FindingResponse, FindingUpdate
from app.security.rbac import require_minimum_role
from app.dependencies import get_current_user
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/findings", tags=["Findings"])

@router.get("", response_model=List[FindingResponse])
def list_findings(
    project_id: Optional[int] = Query(None),
    severity: Optional[FindingSeverity] = Query(None),
    status: Optional[FindingStatus] = Query(None),
    confidence: Optional[FindingConfidence] = Query(None),
    category: Optional[str] = Query(None, description="Category or Rule prefix filter"),
    search: Optional[str] = Query(None, description="Search finding title, description, or rule ID"),
    sort_by: Optional[str] = Query("discovered_at", description="Field to sort by: discovered_at, severity, title, status"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Finding)
    if project_id:
        query = query.filter(Finding.project_id == project_id)
    if severity:
        query = query.filter(Finding.severity == severity)
    if status:
        query = query.filter(Finding.status == status)
    if confidence:
        query = query.filter(Finding.confidence == confidence)
    if category:
        cat_pattern = f"%{category.upper()}%"
        query = query.filter(
            (Finding.rule_id.ilike(cat_pattern)) |
            (Finding.title.ilike(cat_pattern))
        )
    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.filter(
            (Finding.title.ilike(search_pattern)) |
            (Finding.description.ilike(search_pattern)) |
            (Finding.rule_id.ilike(search_pattern))
        )

    # Sorting
    if sort_by == "severity":
        sort_col = Finding.severity
    elif sort_by == "title":
        sort_col = Finding.title
    elif sort_by == "status":
        sort_col = Finding.status
    else:
        sort_col = Finding.discovered_at

    if sort_order == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    return query.offset(skip).limit(limit).all()

@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")
    return finding

@router.post("", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
def create_finding(
    finding_in: FindingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == finding_in.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    new_finding = Finding(
        project_id=finding_in.project_id,
        endpoint_id=finding_in.endpoint_id,
        rule_id=finding_in.rule_id,
        title=finding_in.title,
        description=finding_in.description,
        severity=finding_in.severity,
        confidence=finding_in.confidence,
        status=finding_in.status or FindingStatus.OPEN,
        evidence=finding_in.evidence,
        impact=finding_in.impact,
        remediation=finding_in.remediation
    )
    db.add(new_finding)
    db.commit()
    db.refresh(new_finding)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="FINDING_CREATE",
        resource_type="Finding",
        resource_id=str(new_finding.id),
        details={"title": new_finding.title, "severity": new_finding.severity.value}
    )
    return new_finding

@router.patch("/{finding_id}", response_model=FindingResponse)
def update_finding_status(
    finding_id: int,
    finding_update: FindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    old_status = finding.status.value if finding.status else "UNKNOWN"

    if finding_update.title is not None:
        finding.title = finding_update.title
    if finding_update.description is not None:
        finding.description = finding_update.description
    if finding_update.severity is not None:
        finding.severity = finding_update.severity
    if finding_update.confidence is not None:
        finding.confidence = finding_update.confidence
    if finding_update.evidence is not None:
        finding.evidence = finding_update.evidence
    if finding_update.impact is not None:
        finding.impact = finding_update.impact
    if finding_update.remediation is not None:
        finding.remediation = finding_update.remediation

    if finding_update.status is not None:
        finding.status = finding_update.status
        if finding_update.status == FindingStatus.RESOLVED:
            finding.resolved_at = datetime.utcnow()
        elif finding.status != FindingStatus.RESOLVED:
            finding.resolved_at = None

    db.commit()
    db.refresh(finding)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="FINDING_STATUS_CHANGE",
        resource_type="Finding",
        resource_id=str(finding.id),
        details={"old_status": old_status, "new_status": finding.status.value}
    )
    return finding

# Specific finding lifecycle state transition endpoints
@router.post("/{finding_id}/resolve", response_model=FindingResponse)
def resolve_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    return update_finding_status(finding_id, FindingUpdate(status=FindingStatus.RESOLVED), db, current_user)

@router.post("/{finding_id}/confirm", response_model=FindingResponse)
def confirm_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    return update_finding_status(finding_id, FindingUpdate(status=FindingStatus.CONFIRMED), db, current_user)

@router.post("/{finding_id}/false-positive", response_model=FindingResponse)
def mark_false_positive_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    return update_finding_status(finding_id, FindingUpdate(status=FindingStatus.FALSE_POSITIVE), db, current_user)

@router.post("/{finding_id}/reopen", response_model=FindingResponse)
def reopen_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    return update_finding_status(finding_id, FindingUpdate(status=FindingStatus.OPEN), db, current_user)
