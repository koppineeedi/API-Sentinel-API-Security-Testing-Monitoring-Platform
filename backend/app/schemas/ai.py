from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AIAnalysisCreate(BaseModel):
    finding_id: int

class AIAnalysisResponse(BaseModel):
    id: int
    finding_id: int
    summary: str
    root_cause: Optional[str] = None
    custom_remediation: Optional[str] = None
    risk_score: float
    model_used: str
    created_at: datetime

    class Config:
        from_attributes = True
