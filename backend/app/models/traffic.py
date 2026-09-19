from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("api_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    request_method = Column(String, nullable=False, index=True)
    request_url = Column(String, nullable=False)
    headers = Column(JSON, nullable=True)
    payload = Column(Text, nullable=True) # Omitted or sanitized by default for privacy
    
    response_status = Column(Integer, nullable=False, index=True)
    response_time_ms = Column(Float, nullable=False)
    request_size_bytes = Column(Integer, default=0, nullable=False)
    response_size_bytes = Column(Integer, default=0, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    client_ip = Column(String, nullable=True)
    
    anomaly_score = Column(Float, default=0.0, nullable=False, index=True)
    flag_reasons = Column(JSON, nullable=True) # list of explainable anomaly flags e.g. ["Latency Spike > 3000ms", "401 Burst"]

    project = relationship("APIProject", back_populates="traffic_events")
    endpoint = relationship("APIEndpoint", back_populates="traffic_events")
