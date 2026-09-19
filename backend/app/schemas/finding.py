from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.enums import FindingSeverity, FindingStatus, FindingConfidence

class FindingEvidenceResponse(BaseModel):
    id: int
    finding_id: int
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    payload: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FindingBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: FindingSeverity = FindingSeverity.MEDIUM
    confidence: FindingConfidence = FindingConfidence.MEDIUM
    status: FindingStatus = FindingStatus.OPEN
    evidence: Optional[str] = None
    impact: Optional[str] = None
    remediation: Optional[str] = None

class FindingCreate(FindingBase):
    project_id: int
    endpoint_id: Optional[int] = None
    rule_id: Optional[str] = None

class FindingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[FindingSeverity] = None
    confidence: Optional[FindingConfidence] = None
    status: Optional[FindingStatus] = None
    evidence: Optional[str] = None
    impact: Optional[str] = None
    remediation: Optional[str] = None

class FindingResponse(FindingBase):
    id: int
    project_id: int
    endpoint_id: Optional[int] = None
    rule_id: Optional[str] = None
    discovered_at: datetime
    resolved_at: Optional[datetime] = None
    evidence_records: List[FindingEvidenceResponse] = []

    class Config:
        from_attributes = True
