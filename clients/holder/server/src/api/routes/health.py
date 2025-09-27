from api.schemas.response import HealthResponse
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status=200, message="OK")