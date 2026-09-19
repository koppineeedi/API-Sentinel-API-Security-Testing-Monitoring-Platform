from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models.scan import Scan
from app.models.project import APIProject
from app.models.endpoint import APIEndpoint
from app.models.finding import Finding, FindingEvidence
from app.models.user import User
from app.models.enums import UserRole, ScanStatus, FindingSeverity, FindingStatus, FindingConfidence
from app.schemas.scan import ScanCreate, ScanResponse
from app.security.rbac import require_minimum_role
from app.dependencies import get_current_user
from app.utils.audit_logger import log_audit_event

from scanner.orchestrator import SecurityScanner
from scanner.base import ScannerContext, ScannerMode, TargetEndpoint

router = APIRouter(prefix="/scans", tags=["Scans"])

def run_background_scan(scan_id: int):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan or scan.status == ScanStatus.CANCELLED:
            return
            
        scan.status = ScanStatus.RUNNING
        scan.progress = 10
        scan.started_at = datetime.utcnow()
        db.commit()

        # Check cancellation
        db.refresh(scan)
        if scan.status == ScanStatus.CANCELLED:
            return

        # Load project endpoints
        endpoints = db.query(APIEndpoint).filter(APIEndpoint.project_id == scan.project_id).all()
        target_endpoints = [
            TargetEndpoint(path=ep.path, method=ep.method, parameters=ep.parameters, headers=ep.headers)
            for ep in endpoints
        ]

        mode = ScannerMode.ACTIVE_AUTHORIZED if scan.scan_type in ["FULL", "ACTIVE", "BOLA_ONLY"] else ScannerMode.PASSIVE

        context = ScannerContext(
            target_url=scan.target_url,
            mode=mode,
            endpoints=target_endpoints,
            max_burst_requests=5,
            timeout_seconds=5.0
        )

        scan.progress = 30
        db.commit()

        # Check cancellation before scanner run
        db.refresh(scan)
        if scan.status == ScanStatus.CANCELLED:
            return

        # Run Scanner Orchestrator
        orchestrator = SecurityScanner()
        results = orchestrator.run_all(context)

        # Check cancellation after scanner run
        db.refresh(scan)
        if scan.status == ScanStatus.CANCELLED:
            return

        scan.progress = 70
        db.commit()

        # Persist scanner results as Finding records
        for res in results:
            try:
                sev_enum = FindingSeverity[res.severity.upper()]
            except KeyError:
                sev_enum = FindingSeverity.MEDIUM

            try:
                conf_enum = FindingConfidence[res.confidence.upper()]
            except KeyError:
                conf_enum = FindingConfidence.MEDIUM

            matched_ep = next((ep for ep in endpoints if ep.path == res.endpoint and ep.method == res.http_method), None)

            f = Finding(
                project_id=scan.project_id,
                endpoint_id=matched_ep.id if matched_ep else None,
                rule_id=res.rule_id,
                title=res.title,
                description=res.description,
                severity=sev_enum,
                confidence=conf_enum,
                status=FindingStatus.OPEN,
                evidence=res.evidence,
                impact=res.impact,
                remediation=res.remediation
            )
            db.add(f)
            db.flush()

            fe = FindingEvidence(
                finding_id=f.id,
                request_data={"method": res.http_method, "path": res.endpoint},
                response_data=None,
                payload=res.evidence,
                headers=None
            )
            db.add(fe)

        total_findings = db.query(Finding).filter(Finding.project_id == scan.project_id).count()
        scan.findings_count = total_findings
        scan.progress = 100
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        if scan and scan.status != ScanStatus.CANCELLED:
            scan.status = ScanStatus.FAILED
            scan.progress = 100
            db.commit()
    finally:
        db.close()

@router.get("", response_model=List[ScanResponse])
def list_scans(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Scan)
    if project_id:
        query = query.filter(Scan.project_id == project_id)
    return query.order_by(Scan.created_at.desc()).all()

@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def trigger_scan(
    scan_in: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == scan_in.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    new_scan = Scan(
        project_id=scan_in.project_id,
        name=scan_in.name,
        target_url=scan_in.target_url or project.target_url,
        scan_type=scan_in.scan_type,
        status=ScanStatus.QUEUED,
        progress=0,
        findings_count=0,
        created_by_id=current_user.id
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="SCAN_TRIGGERED",
        resource_type="Scan",
        resource_id=str(new_scan.id),
        details={"project_id": project.id, "target_url": new_scan.target_url, "scan_type": scan_in.scan_type}
    )

    background_tasks.add_task(run_background_scan, new_scan.id)
    return new_scan

@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan

@router.post("/{scan_id}/cancel", response_model=ScanResponse)
def cancel_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    if scan.status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel scan in {scan.status.value} state")

    old_status = scan.status.value
    scan.status = ScanStatus.CANCELLED
    db.commit()
    db.refresh(scan)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="SCAN_CANCELLED",
        resource_type="Scan",
        resource_id=str(scan.id),
        details={"old_status": old_status, "new_status": scan.status.value}
    )
    return scan
