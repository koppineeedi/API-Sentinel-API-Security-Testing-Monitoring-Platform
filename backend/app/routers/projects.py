from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import APIProject
from app.models.endpoint import APIEndpoint
from app.models.finding import Finding
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.security.rbac import require_minimum_role
from app.dependencies import get_current_user
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/projects", tags=["API Projects"])

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = db.query(APIProject).order_by(APIProject.created_at.desc()).all()
    results = []
    for proj in projects:
        ep_count = db.query(APIEndpoint).filter(APIEndpoint.project_id == proj.id).count()
        f_count = db.query(Finding).filter(Finding.project_id == proj.id).count()
        resp = ProjectResponse(
            id=proj.id,
            name=proj.name,
            description=proj.description,
            target_url=proj.target_url,
            created_by_id=proj.created_by_id,
            created_at=proj.created_at,
            updated_at=proj.updated_at,
            endpoints_count=ep_count,
            findings_count=f_count
        )
        results.append(resp)
    return results

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = APIProject(
        name=project_in.name,
        description=project_in.description,
        target_url=project_in.target_url,
        created_by_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="PROJECT_CREATE",
        resource_type="APIProject",
        resource_id=str(project.id),
        details={"name": project.name, "target_url": project.target_url}
    )
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        target_url=project.target_url,
        created_by_id=project.created_by_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        endpoints_count=0,
        findings_count=0
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(APIProject).filter(APIProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    ep_count = db.query(APIEndpoint).filter(APIEndpoint.project_id == project.id).count()
    f_count = db.query(Finding).filter(Finding.project_id == project.id).count()
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        target_url=project.target_url,
        created_by_id=project.created_by_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        endpoints_count=ep_count,
        findings_count=f_count
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="PROJECT_DELETE",
        resource_type="APIProject",
        resource_id=str(project_id)
    )
    return None
