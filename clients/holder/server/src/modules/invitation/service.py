import asyncio
import json
import base64
import urllib.parse
from aries_cloudcontroller import AcaPyClient
from modules.config.settings import settings

def get_client() -> AcaPyClient:
    admin_url = settings.admin_url
    api_key = settings.api_key

    if not admin_url:
        raise ValueError("ACAPY_ADMIN_URL not configured")

    return AcaPyClient(
        admin_url, 
        api_key=api_key if api_key else None
    )

async def create_did(alias: str = None) -> dict | str:
    try:
        result = await get_client().wallet.create_did(body={"key_type": "ed25519"})
                
        did_info = result.result.to_dict()
        
        return {
            'did': did_info.get('did'),
            'verkey': did_info.get('verkey'),
            'metadata': did_info.get('metadata', {}),
            'alias': alias
        }
    except Exception as e:
        print(e)
        return "DID_CREATION_FAILED"

#async def register_did_on_ledger(did, verkey, alias=None) -> bool:
#    try:
#        result = await get_client().ledger.register_nym(
#            did=did,
#            verkey=verkey,
#            alias=alias,
#            role=None
#        )
#        
#        print(f"Registered DID {did} on ledger")
#        return True
#    except Exception as e:
#        print(f"Failed to register DID on ledger: {str(e)}")
#        return False

async def parse_invitation_url(invitation_url: str) -> dict | str:
    try:
        parsed_url = urllib.parse.urlparse(invitation_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        invitation_data = None
        
        if 'c_i' in query_params:
            invitation_b64 = query_params['c_i'][0]
            
            try:
                padding = len(invitation_b64) % 4
                if padding:
                    invitation_b64 += '=' * (4 - padding)
                
                invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                invitation_data = json.loads(invitation_json)
            except Exception:
                return "INVITATION_DECODE_FAILED"
            
        elif 'oob' in query_params:
            invitation_b64 = query_params['oob'][0]
            
            try:
                padding = len(invitation_b64) % 4
                if padding:
                    invitation_b64 += '=' * (4 - padding)
                
                invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                invitation_data = json.loads(invitation_json)
            except Exception as e:
                print(e)
                return "INVITATION_DECODE_FAILED"
            
        elif 'd_m' in query_params:
            invitation_b64 = query_params['d_m'][0]
            
            
            try:
                padding = len(invitation_b64) % 4
                if padding:
                    invitation_b64 += '=' * (4 - padding)
                
                invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                invitation_data = json.loads(invitation_json)
            except Exception:
                return "INVITATION_DECODE_FAILED"
            
        else:
            if parsed_url.query:
                try:
                    padding = len(parsed_url.query) % 4
                    query_with_padding = parsed_url.query + ('=' * (4 - padding) if padding else '')
                    invitation_json = base64.urlsafe_b64decode(query_with_padding).decode('utf-8')
                    invitation_data = json.loads(invitation_json)
                except Exception:
                    try:
                        invitation_data = json.loads(urllib.parse.unquote(parsed_url.query))
                    except Exception:
                        return "INVITATION_PARSE_FAILED"
            else:
                if '?' not in invitation_url and '=' in invitation_url:
                    try:
                        potential_b64 = invitation_url.split('/')[-1] if '/' in invitation_url else invitation_url
                        padding = len(potential_b64) % 4
                        if padding:
                            potential_b64 += '=' * (4 - padding)
                        
                        invitation_json = base64.urlsafe_b64decode(potential_b64).decode('utf-8')
                        invitation_data = json.loads(invitation_json)
                    except Exception:
                        return "INVITATION_URL_INVALID"
                else:
                    return "INVITATION_URL_INVALID"
        
        if not invitation_data:
            return "INVITATION_DATA_NOT_FOUND"
            
        return invitation_data
    except Exception:
        return "INVITATION_PROCESSING_FAILED"

async def prepare_receive_invitation_payload(connection_alias: str, invitation_url: str) -> dict | str:
    try:
        invitation_data = await parse_invitation_url(invitation_url)
        
        if isinstance(invitation_data, str):
            return invitation_data
        
        payload = {
            "invitation": invitation_data,
            "auto_accept": True,
            "alias": connection_alias
        }
        
        return payload
    except Exception:
        return "INVITATION_PAYLOAD_PREPARATION_FAILED"

async def receive_invitation(invitation_payload: dict) -> dict | str:
    try:
        result = await get_client().out_of_band.receive_invitation(
            body=invitation_payload["invitation"],
            alias=invitation_payload.get("alias"),
            auto_accept=invitation_payload.get("auto_accept", True)
        )
        
        connection_info = result.to_dict() if hasattr(result, 'to_dict') else result
        
        return connection_info

    except Exception as e:
        print(e)
        return "INVITATION_RECEIVE_FAILED"
