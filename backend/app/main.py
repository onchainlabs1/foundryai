import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import evidence, reports, systems, fria, controls, incidents, compliance_suite, debug, templates, documents
from app.core.config import settings
from app.core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from app.database import Base, SessionLocal, engine
from app.models import Organization
from app.services.s3 import s3_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Validate critical configuration
    if settings.SECRET_KEY == "change_me" or len(settings.SECRET_KEY) < 16:
        raise ValueError(
            "SECRET_KEY must be set and >= 16 chars. "
            "Set via environment variable SECRET_KEY."
        )
    
    # Create tables (including artifact_text if missing)
    # Check if artifact_text exists, if not create all tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if "artifact_text" not in existing_tables:
        print("Creating missing tables (including artifact_text)...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created")
    else:
        # Ensure all other tables exist too
        Base.metadata.create_all(bind=engine)

    # Seed organization if configured
    if settings.ORG_NAME and settings.ORG_API_KEY:
        db = SessionLocal()
        try:
            # Check if org with this API key exists
            existing = db.query(Organization).filter(
                Organization.api_key == settings.ORG_API_KEY
            ).first()
            
            if not existing:
                # Check if org with this name exists (update key)
                existing_by_name = db.query(Organization).filter(
                    Organization.name == settings.ORG_NAME
                ).first()
                
                if existing_by_name:
                    # Update API key
                    existing_by_name.api_key = settings.ORG_API_KEY
                    db.commit()
                    print(f"Updated organization API key: {settings.ORG_NAME} ({settings.ORG_API_KEY})")
                else:
                    # Create new org
                    org = Organization(name=settings.ORG_NAME, api_key=settings.ORG_API_KEY)
                    db.add(org)
                    db.commit()
                    print(f"Seeded organization: {settings.ORG_NAME} ({settings.ORG_API_KEY})")
            else:
                print(f"Organization already exists: {settings.ORG_NAME} ({settings.ORG_API_KEY})")
        finally:
            db.close()

    # Initialize templates
    from app.api.routes.templates import initialize_templates
    initialize_templates()

    yield


app = FastAPI(
    title="AIMS Readiness API",
    description="ISO/IEC 42001 + EU AI Act compliance platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - restrict to frontend origin in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN != "http://localhost:3001" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware, rate_limit=settings.RATE_LIMIT)

# Routes
app.include_router(systems.router)
app.include_router(evidence.router)
app.include_router(reports.router)
app.include_router(fria.router)
app.include_router(fria.static_router)
app.include_router(controls.router, prefix="/controls")
app.include_router(incidents.router)
app.include_router(compliance_suite.router)
app.include_router(debug.router)
app.include_router(templates.router)
app.include_router(documents.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with structured JSON response."""
    request_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "request_id": request_id,
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with structured JSON response."""
    request_id = str(uuid.uuid4())
    # Don't expose internal errors in production
    error_detail = str(exc) if settings.SECRET_KEY == "change_me" else "Internal server error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "request_id": request_id,
            "error": "Internal Server Error",
            "detail": error_detail,
        },
    )


@app.get("/health")
async def health():
    """Static health check endpoint."""
    return {"status": "ok"}


@app.get("/ready")
async def readiness():
    """
    Readiness probe - checks DB and S3 connectivity.
    
    Returns 200 if all systems operational, 503 otherwise.
    """
    checks = {"database": False, "s3": False}
    
    # Check database
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = True
    except Exception as e:
        checks["database_error"] = str(e)
    
    # Check S3 if configured
    if settings.use_s3:
        checks["s3"] = s3_service.health_check()
    else:
        checks["s3"] = "not_configured"
    
    # Determine overall status
    is_ready = checks["database"] and (checks["s3"] is True or checks["s3"] == "not_configured")
    
    return JSONResponse(
        status_code=200 if is_ready else 503,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
        },
    )

