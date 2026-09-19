from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import ScanStatus

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("api_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    scan_type = Column(String, default="FULL", nullable=False) # e.g., FULL, PASSIVE, ACTIVE, BOLA_ONLY
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False, index=True)
    progress = Column(Integer, default=0, nullable=False) # 0 to 100
    findings_count = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("APIProject", back_populates="scans")
    created_by = relationship("User", back_populates="scans")
