from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.audit import AuditLogResponse
from app.security.rbac import require_minimum_role

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None, description="Action filter e.g. FINDING_STATUS_CHANGE, SCAN_TRIGGERED"),
    search: Optional[str] = Query(None, description="Search resource ID or action details"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_minimum_role(UserRole.SECURITY_ANALYST))
):
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            (AuditLog.action.ilike(pattern)) |
            (AuditLog.resource_type.ilike(pattern)) |
            (AuditLog.resource_id.ilike(pattern))
        )
    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
