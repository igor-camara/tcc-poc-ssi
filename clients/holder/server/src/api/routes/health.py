from api.schemas.response import SuccessResponse
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=SuccessResponse)
def health_check() -> SuccessResponse:
    return SuccessResponse(data="API em funcionamento")