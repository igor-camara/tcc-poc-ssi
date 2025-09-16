"""
SSI (Self-Sovereign Identity) routes for FastAPI
"""
import asyncio
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import (
    ConnectionInvitationRequest, InvitationResponse, ReceiveInvitationPayload
)
from app.models.user import User
from app.auth import get_current_user
from app.services.ssi_service import get_ssi_service

router = APIRouter(tags=["ssi"])

@router.post("/debug-invitation-url")
async def debug_invitation_url(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Debug endpoint to analyze invitation URL structure
    """
    try:
        invitation_url = request.get('invitation_url') or request.get('url')
        
        if not invitation_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invitation_url ou url é obrigatório"
            )
        
        import urllib.parse
        
        parsed_url = urllib.parse.urlparse(invitation_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        return {
            "original_url": invitation_url,
            "parsed_components": {
                "scheme": parsed_url.scheme,
                "netloc": parsed_url.netloc,
                "path": parsed_url.path,
                "query": parsed_url.query,
                "fragment": parsed_url.fragment
            },
            "query_parameters": {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
            "has_c_i": 'c_i' in query_params,
            "has_oob": 'oob' in query_params,
            "has_d_m": 'd_m' in query_params,
            "suggestions": [
                "URL deve conter parâmetro c_i, oob ou d_m com dados codificados em base64",
                "Verifique se a URL não foi truncada ou modificada",
                "Formato esperado: http://example.com?c_i=<base64_data>"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/prepare-invitation", response_model=ReceiveInvitationPayload)
async def prepare_connection_invitation(
    request: ConnectionInvitationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Prepare invitation data for use with /receive-invitation endpoint
    
    This endpoint receives a connection alias and invitation URL, processes the URL
    to extract the invitation data, and returns a payload ready to be used with
    the /receive-invitation endpoint.
    """
    try:
        ssi_service = get_ssi_service()
        
        # Prepare the payload for receive-invitation
        payload = await ssi_service.prepare_receive_invitation_payload(
            request.connection_alias,
            request.invitation_url
        )
        
        return ReceiveInvitationPayload(**payload)
        
    except Exception as e:
        print(f"Prepare invitation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/receive-invitation", response_model=InvitationResponse)
async def receive_connection_invitation(
    request: dict,  # Accept raw dict to handle different parameter names
    current_user: User = Depends(get_current_user)
):
    """
    Process and accept a connection invitation
    
    This endpoint receives a connection alias and invitation URL, processes the
    invitation, and automatically accepts the connection.
    
    Accepts both formats:
    - {"connection_alias": "name", "invitation_url": "url"}
    - {"issuer_name": "name", "url": "url"}
    """
    try:
        # Handle different parameter names from frontend/backend
        connection_alias = request.get('connection_alias') or request.get('issuer_name')
        invitation_url = request.get('invitation_url') or request.get('url')
        
        if not connection_alias or not invitation_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parâmetros obrigatórios: connection_alias/issuer_name e invitation_url/url"
            )
        
        ssi_service = get_ssi_service()
        
        # Prepare the payload
        payload = await ssi_service.prepare_receive_invitation_payload(
            connection_alias,
            invitation_url
        )
        
        # Receive the invitation
        connection_result = await ssi_service.receive_invitation(payload)
        
        return InvitationResponse(
            success=True,
            connection_id=connection_result.get('connection_id'),
            invitation_data=payload.get('invitation'),
            message=f"Convite aceito com sucesso para '{connection_alias}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Receive invitation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar convite: {str(e)}"
        )