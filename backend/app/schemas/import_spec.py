from pydantic import BaseModel, Field
from typing import Optional

class ImportTextRequest(BaseModel):
    content: str = Field(..., description="OpenAPI specification in raw JSON or YAML format")
    project_name: Optional[str] = None

class ImportUrlRequest(BaseModel):
    url: str = Field(..., description="OpenAPI spec URL on explicitly authorized target server")
    allow_local: bool = True
