from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.security.rbac import require_roles
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    return db.query(User).order_by(User.id.asc()).all()

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_update.full_name is not None:
        target_user.full_name = user_update.full_name
    if user_update.role is not None:
        target_user.role = user_update.role
    if user_update.is_active is not None:
        target_user.is_active = user_update.is_active
        
    db.commit()
    db.refresh(target_user)
    
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="USER_UPDATE",
        resource_type="User",
        resource_id=str(target_user.id),
        details={"updated_fields": user_update.dict(exclude_unset=True)}
    )
    return target_user
