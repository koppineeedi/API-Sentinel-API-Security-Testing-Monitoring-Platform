from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import APIProject
from app.models.user import User
from app.risk.engine import RiskEngine
from app.dependencies import get_current_user

router = APIRouter(prefix="/risk", tags=["Risk Engine"])

@router.get("/score/{project_id}", response_model=Dict[str, Any])
def get_project_risk_score(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(APIProject).filter(APIProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    score_report = RiskEngine.calculate_project_risk_score(db, project_id)
    score_report["project_name"] = project.name
    score_report["target_url"] = project.target_url
    return score_report
