from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import ScanStatus

class ScanBase(BaseModel):
    name: str
    target_url: str
    scan_type: str = "FULL"

class ScanCreate(ScanBase):
    project_id: int

class ScanUpdate(BaseModel):
    status: Optional[ScanStatus] = None
    progress: Optional[int] = None
    findings_count: Optional[int] = None

class ScanResponse(ScanBase):
    id: int
    project_id: int
    status: ScanStatus
    progress: int
    findings_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
