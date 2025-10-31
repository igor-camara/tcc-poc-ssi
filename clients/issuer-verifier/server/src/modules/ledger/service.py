import httpx
import logging
import os
from modules.client.service import AcaPyClient
from modules.config.settings import settings
from modules.ledger.schemas import LedgerRegisterResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def register_did_on_governance(key: str) -> dict:
    try:
        logging.info("Creating local DID...")
        did_info = AcaPyClient.did.create(method="sov", key_type="ed25519")
        
        if not did_info:
            logging.error("Failed to create local DID")
            return {"error": "Failed to create local DID"}
        
        logging.info(f"DID created successfully: {did_info.get('did')}")
        
        endpoint = f"{settings.governance_url}/api/ledger/register"
        
        payload = {
            "did": did_info.get("did"),
            "verkey": did_info.get("verkey"),
            "acapy_admin_url": settings.admin_url
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": key
        }
        
        logging.info(f"Registering DID with governance application at {endpoint}")
        response = httpx.post(endpoint, json=payload, headers=headers, timeout=30.0)
        
        if response.status_code == 200 or response.status_code == 201:
            logging.info("DID registered successfully with governance application")
            result = response.json()
            
            os.environ["GOVERNANCE_API_KEY"] = key
            logging.info("API Key stored in environment variables")
            
            logging.info(f"Marking DID {did_info.get('did')} as public...")
            public_result = AcaPyClient.did.set_public_did(did_info.get('did'))
            
            if public_result:
                logging.info(f"DID {did_info.get('did')} successfully marked as public")
                result["public_did"] = public_result
            else:
                logging.warning(f"Failed to mark DID {did_info.get('did')} as public")
                result["public_did_error"] = "Failed to mark DID as public"
            
            return result
        else:
            if response.json().get("detail") == "Cliente já possui DID registrado":
                os.environ["GOVERNANCE_API_KEY"] = key
                logging.info("API Key stored in environment variables")
                return {"message": "DID already registered with governance application"}
            logging.error(f"Failed to register DID. Status: {response.status_code}, Response: {response.text}")
            return {"error": response.json().get("detail", "Failed to register DID with governance")}
            
    except httpx.RequestError as e:
        logging.error(f"Connection error with governance application: {e}")
        return {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        logging.exception(f"Unexpected error during DID registration: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


def check_governance_key() -> dict:
    key = os.environ.get("GOVERNANCE_API_KEY") or settings.governance_api_key
    
    if key and key.strip():
        logging.info("Governance API Key is configured")
        return {
            "configured": True,
            "message": "Governance API Key is configured"
        }
    else:
        logging.info("Governance API Key is not configured")
        return {
            "configured": False,
            "message": "Governance API Key is not configured"
        }
