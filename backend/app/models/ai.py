from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    custom_remediation = Column(Text, nullable=True)
    risk_score = Column(Float, nullable=False, default=5.0) # 0.0 to 10.0 CVSS-style
    model_used = Column(String, default="Sentinel-AI-v1", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    finding = relationship("Finding", back_populates="ai_analysis")
