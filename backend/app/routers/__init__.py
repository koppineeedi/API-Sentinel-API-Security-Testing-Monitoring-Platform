from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.projects import router as projects_router
from app.routers.endpoints import router as endpoints_router
from app.routers.scans import router as scans_router
from app.routers.findings import router as findings_router
from app.routers.traffic import router as traffic_router
from app.routers.rules import router as rules_router
from app.routers.reports import router as reports_router
from app.routers.audit import router as audit_router
from app.routers.ai import router as ai_router

__all__ = [
    "auth_router",
    "users_router",
    "projects_router",
    "endpoints_router",
    "scans_router",
    "findings_router",
    "traffic_router",
    "rules_router",
    "reports_router",
    "audit_router",
    "ai_router"
]
