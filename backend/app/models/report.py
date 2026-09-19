from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("api_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    report_type = Column(String, default="EXECUTIVE_SUMMARY", nullable=False) # EXECUTIVE_SUMMARY, TECHNICAL_DETAILED, COMPLIANCE
    format = Column(String, default="PDF", nullable=False) # PDF, HTML, JSON, CSV
    file_path = Column(String, nullable=True)
    metadata_info = Column(JSON, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("APIProject", back_populates="reports")
    created_by = relationship("User", back_populates="reports")
