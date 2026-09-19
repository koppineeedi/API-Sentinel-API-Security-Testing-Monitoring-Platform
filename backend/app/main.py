from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.models import SecurityRule, FindingSeverity, User, UserRole
from app.security.hashing import get_password_hash
from app.routers import (
    auth_router,
    users_router,
    projects_router,
    endpoints_router,
    scans_router,
    findings_router,
    traffic_router,
    rules_router,
    reports_router,
    audit_router,
    ai_router
)
from app.routers.import_api import router as import_router
from app.routers.risk import router as risk_router
from app.routers.websocket import router as ws_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def seed_initial_data():
    db = SessionLocal()
    try:
        # Seed default security rules
        default_rules = [
            {
                "id": "SEC-BOLA-01",
                "name": "Broken Object Level Authorization (BOLA)",
                "category": "Authorization",
                "severity": FindingSeverity.CRITICAL,
                "description": "Checks whether endpoint resources can be accessed or mutated by modifying object identifiers in URL paths or request parameters without authorization verification.",
                "remediation": "Validate user ownership or role permissions on every object lookup."
            },
            {
                "id": "SEC-AUTH-01",
                "name": "Broken Authentication / JWT Validation Failure",
                "category": "Authentication",
                "severity": FindingSeverity.HIGH,
                "description": "Tests token signing algorithms, expired tokens, or unverified JWT signatures on protected routes.",
                "remediation": "Enforce strong JWT secret verification, restrict allowed algorithms (HS256/RS256), and validate expiration timestamps."
            },
            {
                "id": "SEC-RATE-01",
                "name": "Unrestricted Rate Limiting",
                "category": "Resource Consumption",
                "severity": FindingSeverity.HIGH,
                "description": "Sends rapid request bursts to detect missing rate limits on sensitive authentication or computational endpoints.",
                "remediation": "Implement rate limiting middleware returning HTTP 429 Too Many Requests."
            },
            {
                "id": "SEC-HEAD-01",
                "name": "Missing Security Headers",
                "category": "Security Misconfiguration",
                "severity": FindingSeverity.LOW,
                "description": "Inspects response headers for missing HSTS, CSP, X-Content-Type-Options, and X-Frame-Options.",
                "remediation": "Configure web gateway to return security headers on all API responses."
            },
            {
                "id": "SEC-INJ-01",
                "name": "SQL & Command Injection Vector",
                "category": "Injection",
                "severity": FindingSeverity.CRITICAL,
                "description": "Injects SQL parameters and system command characters into query parameters and JSON payloads.",
                "remediation": "Use parameterized ORM queries and sanitize raw inputs."
            },
            {
                "id": "SEC-INFO-01",
                "name": "Server Information & Technology Disclosure Headers",
                "category": "Information Disclosure",
                "severity": FindingSeverity.LOW,
                "description": "HTTP response reveals specific technology stack details in headers.",
                "remediation": "Remove Server and X-Powered-By response headers at the API gateway."
            },
            {
                "id": "SEC-JWT-01",
                "name": "Insecure JWT Unsigned Algorithm ('alg: none')",
                "category": "Authentication",
                "severity": FindingSeverity.CRITICAL,
                "description": "JWT token uses algorithm 'none', allowing arbitrary unsigned token forgery.",
                "remediation": "Strictly require signature verification and reject 'none' algorithm."
            }
        ]

        for r_data in default_rules:
            existing = db.query(SecurityRule).filter(SecurityRule.id == r_data["id"]).first()
            if not existing:
                rule = SecurityRule(
                    id=r_data["id"],
                    name=r_data["name"],
                    category=r_data["category"],
                    severity=r_data["severity"],
                    description=r_data["description"],
                    remediation=r_data["remediation"],
                    enabled=True
                )
                db.add(rule)
        
        # Seed initial admin user if empty
        if db.query(User).count() == 0:
            admin_user = User(
                email="admin@sentinel.com",
                hashed_password=get_password_hash("AdminPass123!"),
                full_name="System Security Admin",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)

        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

seed_initial_data()

# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(import_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(endpoints_router, prefix=settings.API_V1_STR)
app.include_router(scans_router, prefix=settings.API_V1_STR)
app.include_router(findings_router, prefix=settings.API_V1_STR)
app.include_router(traffic_router, prefix=settings.API_V1_STR)
app.include_router(rules_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "mode": "authorized_testing_only"
    }
