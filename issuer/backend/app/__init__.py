"""
FastAPI application factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.auth import router as auth_router
from app.routers.ssi import router as ssi_router
from app.routers.webhook import router as webhook_router
from app.schemas import HealthResponse
from app.models.user import User
from app.models.ssi_models import DatabaseManager
from datetime import datetime

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database
    User.init_db()
    DatabaseManager.init_ssi_tables()
    
    # Include routers
    app.include_router(auth_router, prefix="/api")
    app.include_router(ssi_router, prefix="/api")
    app.include_router(webhook_router, prefix="/api")
    
    # Health check endpoint
    @app.get("/api/health", response_model=HealthResponse)
    async def health_check():
        """API health check"""
        return HealthResponse(
            status="healthy",
            message="SSI Issuer Backend is running",
            timestamp=datetime.utcnow()
        )
    
    return app