"""
SSI (Self-Sovereign Identity) routes for FastAPI
"""
import asyncio
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import (
    CreateInvitationResponse, CreateSchemaRequest, SchemaResponse,
    CreateCredentialDefinitionRequest, CredentialDefinitionResponse,
    SendCredentialOfferRequest, IssueCredentialRequest,
    ShowUsersResponse, UserConnectionResponse, ShowOffersResponse,
    OfferResponse, CertificateResponse, SuccessResponse
)
from app.models.user import User
from app.models.ssi_models import ConnectionModel, CredentialOfferModel, IssuedCertificateModel
from app.auth import get_current_user
from app.services.ssi_service import get_ssi_service

router = APIRouter(tags=["ssi"])

@router.post("/create-invitation", response_model=CreateInvitationResponse)
async def create_connection_invitation(
    request: dict,  # Accept raw dict to handle different parameter names
    current_user: User = Depends(get_current_user)
):
    """
    Create a connection invitation for the issuer
    """
    try:
        ssi_service = get_ssi_service()
        
        # Get optional parameters
        alias = request.get("alias", f"Issuer-{current_user.email}")
        auto_accept = request.get("auto_accept", True)
        
        # Create invitation
        invitation_data = await ssi_service.create_invitation(
            alias=alias,
            auto_accept=auto_accept
        )
        
        return CreateInvitationResponse(
            connection_id=invitation_data["connection_id"],
            invitation=invitation_data["invitation"],
            invitation_url=invitation_data["invitation_url"],
            alias=alias
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create invitation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar convite: {str(e)}"
        )

@router.post("/create-certificate", response_model=SchemaResponse)
async def create_certificate(
    request: CreateSchemaRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a certificate schema and credential definition
    """
    try:
        ssi_service = get_ssi_service()
        
        # Create schema
        schema_data = await ssi_service.create_schema(
            schema_name=request.schema_name,
            schema_version=request.schema_version,
            attributes=request.attributes,
            created_by=current_user.id
        )
        
        # Create credential definition
        cred_def_data = await ssi_service.create_credential_definition(
            schema_id=schema_data["schema_id"],
            tag="default",
            support_revocation=False
        )
        
        return SchemaResponse(
            schema_id=schema_data["schema_id"],
            schema=schema_data,
            schema_name=request.schema_name,
            schema_version=request.schema_version,
            attributes=request.attributes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create certificate error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar certificado: {str(e)}"
        )

@router.get("/show-users", response_model=ShowUsersResponse)
async def show_users(
    current_user: User = Depends(get_current_user)
):
    """
    Show users that have accepted connection with the issuer
    """
    try:
        ssi_service = get_ssi_service()
        
        # Get active connections
        connections = await ssi_service.get_active_connections()
        
        # Convert to response format
        users = []
        for conn in connections:
            user_response = UserConnectionResponse(
                user_id=conn.user_id or "unknown",
                connection_id=conn.connection_id,
                their_label=conn.their_label,
                their_did=conn.their_did,
                state=conn.state,
                created_at=conn.created_at.isoformat()
            )
            users.append(user_response)
        
        return ShowUsersResponse(
            total_users=len(users),
            users=users
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Show users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar usuários: {str(e)}"
        )

@router.post("/send-offer", response_model=SuccessResponse)
async def send_offer(
    request: SendCredentialOfferRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send credential offer to a user that has opened connection with the issuer
    """
    try:
        ssi_service = get_ssi_service()
        
        # Send credential offer
        exchange_data = await ssi_service.send_credential_offer(
            connection_id=request.connection_id,
            credential_definition_id=request.credential_definition_id,
            credential_preview=request.credential_preview,
            comment=request.comment
        )
        
        return SuccessResponse(
            success=True,
            message="Oferta de credencial enviada com sucesso",
            data={
                "credential_exchange_id": exchange_data["credential_exchange_id"],
                "connection_id": request.connection_id,
                "state": exchange_data.get("state", "offer_sent")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Send offer error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar oferta: {str(e)}"
        )
    
@router.get("/show-offers", response_model=ShowOffersResponse)
async def show_offers(
    current_user: User = Depends(get_current_user)
):
    """
    Show pending offers for the authenticated user
    """
    try:
        ssi_service = get_ssi_service()
        
        # Get all offers
        offers = await ssi_service.get_offers()
        
        # Convert to response format
        offer_responses = []
        pending_count = 0
        completed_count = 0
        
        for offer in offers:
            # Get connection info for label
            connection = ConnectionModel.get_by_connection_id(offer.connection_id)
            their_label = connection.their_label if connection else "Unknown"
            
            offer_response = OfferResponse(
                offer_id=offer.id,
                credential_exchange_id=offer.credential_exchange_id,
                connection_id=offer.connection_id,
                user_id=offer.user_id,
                their_label=their_label,
                credential_definition_id=offer.credential_definition_id,
                schema_name=offer.schema_name,
                state=offer.state,
                attributes=offer.attributes,
                created_at=offer.created_at.isoformat(),
                updated_at=offer.updated_at.isoformat()
            )
            offer_responses.append(offer_response)
            
            # Count by state
            if offer.state in ["offer_sent", "request_received"]:
                pending_count += 1
            elif offer.state in ["credential_issued", "credential_acked"]:
                completed_count += 1
        
        return ShowOffersResponse(
            total_offers=len(offer_responses),
            pending_offers=pending_count,
            completed_offers=completed_count,
            offers=offer_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Show offers error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar ofertas: {str(e)}"
        )

@router.post("/issue-certificate", response_model=SuccessResponse)
async def issue_certificate(
    request: IssueCredentialRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Issue certificate to user that accepted the offer
    """
    try:
        ssi_service = get_ssi_service()
        
        # Issue the credential
        issued_data = await ssi_service.issue_credential(
            credential_exchange_id=request.credential_exchange_id,
            comment=request.comment
        )
        
        return SuccessResponse(
            success=True,
            message="Certificado emitido com sucesso",
            data={
                "credential_exchange_id": request.credential_exchange_id,
                "state": issued_data.get("state", "credential_issued")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Issue certificate error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar certificado: {str(e)}"
        )

@router.get("/show-certificates", response_model=dict)
async def show_certificates(
    current_user: User = Depends(get_current_user)
):
    """
    Show all issued certificates
    """
    try:
        # Get all issued certificates from database
        certificates = IssuedCertificateModel.get_all_certificates()
        
        # Convert to response format
        certificate_responses = []
        for cert in certificates:
            # Get connection info for label
            connection = ConnectionModel.get_by_connection_id(cert.connection_id)
            recipient_label = connection.their_label if connection else "Unknown"
            
            certificate_response = CertificateResponse(
                certificate_id=cert.id,
                credential_exchange_id=cert.credential_exchange_id,
                connection_id=cert.connection_id,
                user_id=cert.user_id,
                recipient_label=recipient_label,
                schema_name=cert.schema_name,
                credential_definition_id=cert.credential_definition_id,
                attributes=cert.attributes,
                state=cert.state,
                issued_at=cert.issued_at.isoformat()
            )
            certificate_responses.append(certificate_response)
        
        return {
            "total_certificates": len(certificate_responses),
            "certificates": [cert.dict() for cert in certificate_responses]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Show certificates error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao buscar certificados: {str(e)}"
        )