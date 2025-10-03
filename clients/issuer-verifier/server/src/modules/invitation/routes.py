from modules.invitation.schema import InvitationRequest, ConnectionResponse
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse
from modules.invitation.service import create_invitation

router = APIRouter(prefix="/invitation", tags=["invitation"])

@router.post("/create-url", response_model=SuccessResponse)
async def create_invitation_url(invitation_request: InvitationRequest):
    
    invitation = await create_invitation(alias=invitation_request.alias)

    connection = ConnectionResponse(
        label=invitation["invitation"]["label"],
        invitation_url=invitation["invitation_url"]
    )
    return JSONResponse(status_code=200, content=SuccessResponse(data=connection).model_dump())