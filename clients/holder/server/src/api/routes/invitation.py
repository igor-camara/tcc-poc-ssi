from api.schemas.response import SuccessResponse
from fastapi import APIRouter

router = APIRouter(prefix="/invitation", tags=["invitation"])

@router.get("/receive-url", response_model=SuccessResponse)
def receive_invitation_url() -> SuccessResponse:
    return SuccessResponse(data="API em funcionamento")