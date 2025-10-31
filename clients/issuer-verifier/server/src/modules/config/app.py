from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

from modules.config.settings import settings
from modules.utils.model import SuccessResponse

from modules.auth import routes as auth_routes
from modules.invitation import routes as invitation_routes
from modules.credential import routes as credential_routes
from modules.connection import routes as connection_routes
from modules.ledger import routes as ledger_routes
from modules.proof import routes as proof_routes
from modules.webhook import routes as webhook_routes

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI()
    app.title = "Holder API"

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    health_router = APIRouter(prefix="/health", tags=["health"])
    
    @health_router.get("", response_model=SuccessResponse)
    def health_check() -> SuccessResponse:
        return SuccessResponse(data="API em funcionamento")

    app.include_router(health_router, prefix="/api")
    app.include_router(auth_routes.router, prefix="/api")
    app.include_router(invitation_routes.router, prefix="/api")
    app.include_router(credential_routes.router, prefix="/api")
    app.include_router(connection_routes.router, prefix="/api")
    app.include_router(ledger_routes.router, prefix="/api")
    app.include_router(proof_routes.router, prefix="/api")
    app.include_router(webhook_routes.router)

    return app