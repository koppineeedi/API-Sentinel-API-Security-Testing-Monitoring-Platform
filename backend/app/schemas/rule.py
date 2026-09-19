from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import FindingSeverity

class SecurityRuleBase(BaseModel):
    name: str
    category: str
    severity: FindingSeverity = FindingSeverity.MEDIUM
    description: Optional[str] = None
    remediation: Optional[str] = None
    enabled: bool = True

class SecurityRuleCreate(SecurityRuleBase):
    id: str # e.g. "SEC-BOLA-01"

class SecurityRuleUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[FindingSeverity] = None
    description: Optional[str] = None
    remediation: Optional[str] = None
    enabled: Optional[bool] = None

class SecurityRuleResponse(SecurityRuleBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
