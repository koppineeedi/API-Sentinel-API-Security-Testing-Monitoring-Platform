from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.rule import SecurityRule
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.rule import SecurityRuleResponse, SecurityRuleUpdate
from app.security.rbac import require_roles
from app.dependencies import get_current_user
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/rules", tags=["Security Rules"])

@router.get("", response_model=List[SecurityRuleResponse])
def list_security_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(SecurityRule).order_by(SecurityRule.id.asc()).all()

@router.patch("/{rule_id}", response_model=SecurityRuleResponse)
def update_security_rule(
    rule_id: str,
    rule_update: SecurityRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    rule = db.query(SecurityRule).filter(SecurityRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

    if rule_update.name is not None:
        rule.name = rule_update.name
    if rule_update.category is not None:
        rule.category = rule_update.category
    if rule_update.severity is not None:
        rule.severity = rule_update.severity
    if rule_update.description is not None:
        rule.description = rule_update.description
    if rule_update.remediation is not None:
        rule.remediation = rule_update.remediation
    if rule_update.enabled is not None:
        rule.enabled = rule_update.enabled

    db.commit()
    db.refresh(rule)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="SECURITY_RULE_UPDATE",
        resource_type="SecurityRule",
        resource_id=rule.id,
        details={"enabled": rule.enabled}
    )
    return rule
