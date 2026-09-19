from datetime import datetime
from typing import Optional, Any, Dict, List
from pydantic import BaseModel

class EndpointBase(BaseModel):
    path: str
    method: str
    description: Optional[str] = None
    parameters: Optional[Any] = None
    headers: Optional[Dict[str, str]] = None

class EndpointCreate(EndpointBase):
    project_id: int

class EndpointUpdate(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Any] = None
    headers: Optional[Dict[str, str]] = None

class EndpointResponse(EndpointBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
