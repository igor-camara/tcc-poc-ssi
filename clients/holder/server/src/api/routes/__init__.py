from fastapi import FastAPI

from . import health
from . import auth

app = FastAPI()
app.include_router(health.router)
app.include_router(auth.router)