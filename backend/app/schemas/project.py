from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_url: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_url: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    endpoints_count: Optional[int] = 0
    findings_count: Optional[int] = 0

    class Config:
        from_attributes = True
