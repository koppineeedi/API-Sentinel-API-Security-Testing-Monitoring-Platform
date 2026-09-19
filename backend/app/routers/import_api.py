from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import APIProject
from app.models.endpoint import APIEndpoint
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.import_spec import ImportTextRequest, ImportUrlRequest
from app.schemas.project import ProjectResponse
from app.services.openapi_parser import OpenAPIParser, OpenAPIDiscoveryResult
from app.security.ssrf import SSRFProtector
from app.security.rbac import require_minimum_role
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/projects", tags=["API Discovery & Import"])

def _process_and_store_spec(db: Session, project: APIProject, spec_result: OpenAPIDiscoveryResult, user_id: int) -> int:
    """
    Populates project base URL and imports extracted endpoints into PostgreSQL database passively.
    """
    if spec_result.base_url:
        project.target_url = spec_result.base_url
    if spec_result.description and not project.description:
        project.description = spec_result.description
    
    imported_count = 0
    for ep in spec_result.endpoints:
        # Avoid duplicate endpoints in project
        existing = db.query(APIEndpoint).filter(
            APIEndpoint.project_id == project.id,
            APIEndpoint.path == ep.path,
            APIEndpoint.method == ep.method
        ).first()

        if not existing:
            new_ep = APIEndpoint(
                project_id=project.id,
                path=ep.path,
                method=ep.method,
                description=ep.summary or ep.description,
                parameters=ep.parameters,
                headers=None
            )
            db.add(new_ep)
            imported_count += 1

    db.commit()
    return imported_count

@router.post("/{project_id}/import/file", response_model=Dict[str, Any])
async def import_spec_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    try:
        raw_bytes = await file.read()
        content = raw_bytes.decode("utf-8")
        parsed = OpenAPIParser.parse(content)
        count = _process_and_store_spec(db, project, parsed, current_user.id)

        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="OPENAPI_IMPORT_FILE",
            resource_type="APIProject",
            resource_id=str(project.id),
            details={"filename": file.filename, "endpoints_imported": count}
        )

        return {
            "message": f"Successfully imported {count} endpoints from OpenAPI specification passively.",
            "project_id": project.id,
            "title": parsed.title,
            "version": parsed.version,
            "endpoints_imported": count
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.post("/{project_id}/import/text", response_model=Dict[str, Any])
def import_spec_text(
    project_id: int,
    payload: ImportTextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    try:
        parsed = OpenAPIParser.parse(payload.content)
        count = _process_and_store_spec(db, project, parsed, current_user.id)

        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="OPENAPI_IMPORT_TEXT",
            resource_type="APIProject",
            resource_id=str(project.id),
            details={"endpoints_imported": count}
        )

        return {
            "message": f"Successfully imported {count} endpoints from raw specification text.",
            "project_id": project.id,
            "title": parsed.title,
            "version": parsed.version,
            "endpoints_imported": count
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.post("/{project_id}/import/url", response_model=Dict[str, Any])
async def import_spec_url(
    project_id: int,
    payload: ImportUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Perform safe HTTP fetch with SSRF validation
    content = await SSRFProtector.fetch_safe_url(payload.url, allow_local=payload.allow_local)

    try:
        parsed = OpenAPIParser.parse(content)
        count = _process_and_store_spec(db, project, parsed, current_user.id)

        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="OPENAPI_IMPORT_URL",
            resource_type="APIProject",
            resource_id=str(project.id),
            details={"source_url": payload.url, "endpoints_imported": count}
        )

        return {
            "message": f"Successfully imported {count} endpoints from remote authorized URL.",
            "project_id": project.id,
            "title": parsed.title,
            "version": parsed.version,
            "endpoints_imported": count
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
