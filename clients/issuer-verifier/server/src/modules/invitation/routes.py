from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse
from modules.invitation.service import create_invitation

router = APIRouter(prefix="/invitation", tags=["invitation"])

@router.post("/create-url", response_model=SuccessResponse)
def create_invitation_url(alias: str):
    invitation = create_invitation(alias=alias)

    return JSONResponse(status_code=200, content=SuccessResponse(data=invitation).model_dump())