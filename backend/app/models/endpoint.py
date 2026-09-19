from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class APIEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("api_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    path = Column(String, index=True, nullable=False)
    method = Column(String, nullable=False, index=True) # GET, POST, PUT, DELETE, PATCH, etc.
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True) # JSON list or dict of parameters
    headers = Column(JSON, nullable=True) # JSON dict of default headers
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    project = relationship("APIProject", back_populates="endpoints")
    findings = relationship("Finding", back_populates="endpoint", cascade="all, delete-orphan")
    traffic_events = relationship("TrafficEvent", back_populates="endpoint")
