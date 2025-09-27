from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.schemas.user import User
from api import settings

from . import health
from . import auth

app = FastAPI()
app.title = "Holder API"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

User.init_db()