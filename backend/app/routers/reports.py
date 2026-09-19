from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.models.project import APIProject
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.report import ReportCreate, ReportResponse
from app.security.rbac import require_minimum_role
from app.dependencies import get_current_user
from app.utils.audit_logger import log_audit_event
from app.services.report_service import ReportGenerator

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=List[ReportResponse])
def list_reports(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Report)
    if project_id:
        query = query.filter(Report.project_id == project_id)
    return query.order_by(Report.created_at.desc()).all()

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == report_in.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    report = Report(
        project_id=report_in.project_id,
        title=report_in.title,
        report_type=report_in.report_type,
        format=report_in.format.upper(),
        file_path=f"/reports/generated_report_{report_in.project_id}_{report_in.format.lower()}",
        metadata_info={
            "generated_by": current_user.email,
            "project_name": project.name,
            "target_url": project.target_url
        },
        created_by_id=current_user.id
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="REPORT_GENERATE",
        resource_type="Report",
        resource_id=str(report.id),
        details={"format": report.format, "project_id": project.id}
    )
    return report

@router.get("/{report_id}/download/html")
def download_html_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    project = db.query(APIProject).filter(APIProject.id == report.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated project not found")

    html_content = ReportGenerator.generate_html_report(db, project, report.title)
    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="sentinel_report_{report.id}.html"'}
    )

@router.get("/{report_id}/download/pdf")
def download_pdf_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    project = db.query(APIProject).filter(APIProject.id == report.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated project not found")

    html_content = ReportGenerator.generate_html_report(db, project, report.title)
    return Response(
        content=html_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="sentinel_report_{report.id}.pdf"'}
    )
