from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from contextlib import asynccontextmanager

from modules.config.settings import settings
from modules.utils.model import SuccessResponse
from modules.clients.routes import router as clients_router
from modules.steward.routes import router as stewards_router
from modules.auth.routes import router as auth_router
from modules.scheduler.routes import router as scheduler_router
from modules.ledger.routes import router as ledger_router
from modules.schemas.routes import router as schemas_router
from modules.utils.scheduler import voting_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Iniciar scheduler de votação
    voting_scheduler.start()
    yield
    # Shutdown: Parar scheduler
    await voting_scheduler.stop()

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
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
    app.include_router(auth_router, prefix="/api")
    app.include_router(clients_router, prefix="/api")
    app.include_router(stewards_router, prefix="/api")
    app.include_router(scheduler_router, prefix="/api")
    app.include_router(ledger_router, prefix="/api")
    app.include_router(schemas_router, prefix="/api")

    return app