from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.endpoint import APIEndpoint
from app.models.project import APIProject
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.endpoint import EndpointCreate, EndpointResponse, EndpointUpdate
from app.security.rbac import require_minimum_role
from app.dependencies import get_current_user
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/endpoints", tags=["API Endpoints"])

@router.get("", response_model=List[EndpointResponse])
def list_endpoints(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(APIEndpoint)
    if project_id:
        query = query.filter(APIEndpoint.project_id == project_id)
    return query.order_by(APIEndpoint.path.asc()).all()

@router.post("", response_model=EndpointResponse, status_code=status.HTTP_201_CREATED)
def create_endpoint(
    endpoint_in: EndpointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    project = db.query(APIProject).filter(APIProject.id == endpoint_in.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    endpoint = APIEndpoint(
        project_id=endpoint_in.project_id,
        path=endpoint_in.path,
        method=endpoint_in.method.upper(),
        description=endpoint_in.description,
        parameters=endpoint_in.parameters,
        headers=endpoint_in.headers
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="ENDPOINT_CREATE",
        resource_type="APIEndpoint",
        resource_id=str(endpoint.id),
        details={"path": endpoint.path, "method": endpoint.method}
    )
    return endpoint

@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    endpoint = db.query(APIEndpoint).filter(APIEndpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")
    
    db.delete(endpoint)
    db.commit()
    return None
