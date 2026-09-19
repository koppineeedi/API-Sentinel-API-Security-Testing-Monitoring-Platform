from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import FindingSeverity, FindingStatus, FindingConfidence

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("api_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id", ondelete="SET NULL"), nullable=True, index=True)
    rule_id = Column(String, ForeignKey("security_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    severity = Column(Enum(FindingSeverity), nullable=False, default=FindingSeverity.MEDIUM, index=True)
    confidence = Column(Enum(FindingConfidence), nullable=False, default=FindingConfidence.MEDIUM)
    status = Column(Enum(FindingStatus), nullable=False, default=FindingStatus.OPEN, index=True)
    
    evidence = Column(Text, nullable=True)
    impact = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)

    project = relationship("APIProject", back_populates="findings")
    endpoint = relationship("APIEndpoint", back_populates="findings")
    rule = relationship("SecurityRule", back_populates="findings")
    evidence_records = relationship("FindingEvidence", back_populates="finding", cascade="all, delete-orphan")
    ai_analysis = relationship("AIAnalysis", back_populates="finding", uselist=False, cascade="all, delete-orphan")

class FindingEvidence(Base):
    __tablename__ = "finding_evidence"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    request_data = Column(JSON, nullable=True) # headers, params, body
    response_data = Column(JSON, nullable=True) # status_code, headers, body
    payload = Column(Text, nullable=True) # specific payload trigger
    headers = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    finding = relationship("Finding", back_populates="evidence_records")
