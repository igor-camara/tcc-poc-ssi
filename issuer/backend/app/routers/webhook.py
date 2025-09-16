"""
Webhook endpoints for ACA-Py events
"""
from fastapi import APIRouter, Request, HTTPException
from app.models.ssi_models import ConnectionModel, CredentialOfferModel, IssuedCertificateModel
from datetime import datetime
import json

router = APIRouter(tags=["webhook"])

@router.post("/webhooks/topic/{topic}/")
async def handle_webhook(topic: str, request: Request):
    """
    Handle ACA-Py webhook events
    
    Args:
        topic: The webhook topic (connections, issue_credential, etc.)
        request: The request object containing the webhook payload
    """
    try:
        # Get the webhook payload
        payload = await request.json()
        print(f"Received webhook for topic '{topic}': {json.dumps(payload, indent=2)}")
        
        # Handle different webhook topics
        if topic == "connections":
            await handle_connection_webhook(payload)
        elif topic == "issue_credential":
            await handle_credential_webhook(payload)
        elif topic == "present_proof":
            await handle_proof_webhook(payload)
        else:
            print(f"Unhandled webhook topic: {topic}")
        
        return {"message": "Webhook processed successfully"}
        
    except Exception as e:
        print(f"Error processing webhook for topic '{topic}': {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {str(e)}")

async def handle_connection_webhook(payload: dict):
    """
    Handle connection webhook events
    
    Args:
        payload: The webhook payload for connection events
    """
    try:
        connection_id = payload.get("connection_id")
        state = payload.get("state")
        
        if not connection_id:
            print("No connection_id in webhook payload")
            return
        
        print(f"Processing connection webhook: {connection_id} -> {state}")
        
        # Get or create connection record
        connection = ConnectionModel.get_by_connection_id(connection_id)
        
        if connection:
            # Update existing connection
            connection.state = state
            connection.their_label = payload.get("their_label", connection.their_label)
            connection.their_did = payload.get("their_did", connection.their_did)
            connection.their_public_did = payload.get("their_public_did", connection.their_public_did)
            connection.my_did = payload.get("my_did", connection.my_did)
            connection.updated_at = datetime.utcnow()
            connection.save()
            print(f"Updated connection {connection_id}")
        else:
            # Create new connection record
            connection = ConnectionModel(
                connection_id=connection_id,
                state=state,
                their_label=payload.get("their_label"),
                their_did=payload.get("their_did"),
                their_public_did=payload.get("their_public_did"),
                my_did=payload.get("my_did"),
                alias=payload.get("alias")
            )
            connection.save()
            print(f"Created new connection {connection_id}")
            
    except Exception as e:
        print(f"Error handling connection webhook: {str(e)}")

async def handle_credential_webhook(payload: dict):
    """
    Handle credential exchange webhook events
    
    Args:
        payload: The webhook payload for credential events
    """
    try:
        credential_exchange_id = payload.get("credential_exchange_id")
        state = payload.get("state")
        connection_id = payload.get("connection_id")
        
        if not credential_exchange_id:
            print("No credential_exchange_id in webhook payload")
            return
        
        print(f"Processing credential webhook: {credential_exchange_id} -> {state}")
        
        # Update offer record if it exists
        offer = CredentialOfferModel.get_by_exchange_id(credential_exchange_id)
        if offer:
            offer.state = state
            offer.updated_at = datetime.utcnow()
            offer.save()
            print(f"Updated offer {credential_exchange_id}")
        
        # If credential was issued, create certificate record
        if state == "credential_issued":
            # Check if certificate record already exists
            certificate = IssuedCertificateModel.get_by_exchange_id(credential_exchange_id)
            if not certificate and offer:
                certificate = IssuedCertificateModel(
                    credential_exchange_id=credential_exchange_id,
                    connection_id=connection_id,
                    credential_definition_id=payload.get("credential_definition_id", ""),
                    schema_name=offer.schema_name,
                    attributes=offer.attributes,
                    state=state,
                    credential_data=payload.get("credential", {})
                )
                certificate.save()
                print(f"Created certificate record {credential_exchange_id}")
        
        # Update certificate record if it exists
        elif state in ["credential_acked", "credential_revoked"]:
            certificate = IssuedCertificateModel.get_by_exchange_id(credential_exchange_id)
            if certificate:
                certificate.state = state
                if state == "credential_revoked":
                    certificate.revoked_at = datetime.utcnow()
                certificate.save()
                print(f"Updated certificate {credential_exchange_id}")
            
    except Exception as e:
        print(f"Error handling credential webhook: {str(e)}")

async def handle_proof_webhook(payload: dict):
    """
    Handle proof presentation webhook events
    
    Args:
        payload: The webhook payload for proof events
    """
    try:
        # For future implementation of proof verification
        print(f"Proof webhook received: {payload}")
        
    except Exception as e:
        print(f"Error handling proof webhook: {str(e)}")

@router.get("/webhook-status")
async def webhook_status():
    """
    Health check for webhook endpoint
    """
    return {
        "status": "active",
        "message": "Webhook endpoint is ready to receive ACA-Py events",
        "supported_topics": ["connections", "issue_credential", "present_proof"]
    }
    