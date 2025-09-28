from modules.invitation.schema import InvitationRequest
from modules.invitation.service import prepare_receive_invitation_payload, receive_invitation
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse

router = APIRouter(prefix="/invitation", tags=["invitation"])

@router.post("/receive-url", response_model=SuccessResponse)
async def receive_invitation_url(invitation_request: InvitationRequest):
    invitation_data = await prepare_receive_invitation_payload(invitation_request.alias, invitation_request.url)

    await receive_invitation(invitation_data)

    return JSONResponse(status_code=200, content=SuccessResponse(data="Conexão criada com sucesso").model_dump())