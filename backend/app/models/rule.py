from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import FindingSeverity

class SecurityRule(Base):
    __tablename__ = "security_rules"

    id = Column(String, primary_key=True, index=True) # e.g. "SEC-BOLA-01"
    name = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False) # e.g. "Authorization", "Injection", "Headers"
    severity = Column(Enum(FindingSeverity), nullable=False, default=FindingSeverity.MEDIUM)
    description = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    findings = relationship("Finding", back_populates="rule")
