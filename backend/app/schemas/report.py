from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ReportCreate(BaseModel):
    project_id: int
    title: str
    report_type: str = "EXECUTIVE_SUMMARY" # EXECUTIVE_SUMMARY, TECHNICAL_DETAILED, COMPLIANCE
    format: str = "PDF" # PDF, HTML, JSON, CSV

class ReportResponse(BaseModel):
    id: int
    project_id: int
    title: str
    report_type: str
    format: str
    file_path: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None
    created_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
