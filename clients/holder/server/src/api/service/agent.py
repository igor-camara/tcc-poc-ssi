import asyncio
import json
import base64
import urllib.parse
from aries_cloudcontroller import AcaPyClient
from api import settings

def get_client() -> AcaPyClient:
    admin_url = settings.admin_url
    api_key = settings.api_key

    if not admin_url:
        raise ValueError("ACAPY_ADMIN_URL not configured")

    return AcaPyClient(
        admin_url, 
        api_key=api_key if api_key else None
    )

async def create_did(alias: str = None) -> dict:
    try:
        result = await get_client().wallet.create_did(body={"key_type": "ed25519"})
                
        did_info = result.result.to_dict()
        
        # print(f"Created DID: {did_info.get('did')} with verkey: {did_info.get('verkey')}")
        
        return {
            'did': did_info.get('did'),
            'verkey': did_info.get('verkey'),
            'metadata': did_info.get('metadata', {}),
            'alias': alias
        }
    except Exception as e:
        raise Exception(f"Erro ao criar DID: {str(e)}")

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

async def parse_invitation_url(invitation_url: str) -> dict:
    try:
        parsed_url = urllib.parse.urlparse(invitation_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        print(f"Parsed URL components: scheme={parsed_url.scheme}, netloc={parsed_url.netloc}, path={parsed_url.path}")
        print(f"Query parameters found: {list(query_params.keys())}")
        
        invitation_data = None
        
        if 'c_i' in query_params:
            print("Found 'c_i' parameter - processing as connection invitation")
            invitation_b64 = query_params['c_i'][0]
            print(f"Base64 invitation data (first 50 chars): {invitation_b64[:50]}...")
            
            try:
                padding = len(invitation_b64) % 4
                if padding:
                    invitation_b64 += '=' * (4 - padding)
                
                invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                invitation_data = json.loads(invitation_json)
                print("Successfully decoded c_i parameter")
            except Exception as decode_error:
                print(f"Failed to decode c_i parameter: {decode_error}")
                raise
            
        elif 'oob' in query_params:
            print("Found 'oob' parameter - processing as out-of-band invitation")
            invitation_b64 = query_params['oob'][0]
            print(f"Base64 invitation data (first 50 chars): {invitation_b64[:50]}...")
            
            try:
                padding = len(invitation_b64) % 4
                if padding:
                    invitation_b64 += '=' * (4 - padding)
                
                invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                invitation_data = json.loads(invitation_json)
                print("Successfully decoded oob parameter")
            except Exception as decode_error:
                print(f"Failed to decode oob parameter: {decode_error}")
                raise
            
        elif 'd_m' in query_params:
            print("Found 'd_m' parameter - processing as DIDComm message")
            invitation_b64 = query_params['d_m'][0]
            print(f"Base64 invitation data (first 50 chars): {invitation_b64[:50]}...")
            
            try:
                padding = len(invitation_b64) % 4
                if padding:
                    invitation_b64 += '=' * (4 - padding)
                
                invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                invitation_data = json.loads(invitation_json)
                print("Successfully decoded d_m parameter")
            except Exception as decode_error:
                print(f"Failed to decode d_m parameter: {decode_error}")
                raise
            
        else:
            if parsed_url.query:
                print(f"No standard invitation parameters found. Raw query: {parsed_url.query}")
                
                try:
                    padding = len(parsed_url.query) % 4
                    query_with_padding = parsed_url.query + ('=' * (4 - padding) if padding else '')
                    invitation_json = base64.urlsafe_b64decode(query_with_padding).decode('utf-8')
                    invitation_data = json.loads(invitation_json)
                    print("Successfully decoded entire query as base64")
                except Exception as decode_error:
                    print(f"Failed to decode query as base64: {decode_error}")
                    
                    try:
                        invitation_data = json.loads(urllib.parse.unquote(parsed_url.query))
                        print("Successfully parsed query as JSON")
                    except Exception as json_error:
                        print(f"Failed to parse query as JSON: {json_error}")
                        raise ValueError(f"Unable to parse invitation from URL. Query: {parsed_url.query}")
            else:
                if '?' not in invitation_url and '=' in invitation_url:
                    print("No query parameters found, trying to decode entire URL as base64")
                    try:
                        potential_b64 = invitation_url.split('/')[-1] if '/' in invitation_url else invitation_url
                        padding = len(potential_b64) % 4
                        if padding:
                            potential_b64 += '=' * (4 - padding)
                        
                        invitation_json = base64.urlsafe_b64decode(potential_b64).decode('utf-8')
                        invitation_data = json.loads(invitation_json)
                        print("Successfully decoded URL as base64")
                    except Exception as decode_error:
                        print(f"Failed to decode URL as base64: {decode_error}")
                        raise ValueError("No invitation data found in URL and unable to decode as base64")
                else:
                    raise ValueError("No invitation data found in URL")
        
        if not invitation_data:
            raise ValueError("No valid invitation data found in URL")
            
        print(f"Successfully parsed invitation: {json.dumps(invitation_data, indent=2)}")
        return invitation_data
    except Exception as e:
        print(f"Failed to parse invitation URL: {str(e)}")
        raise Exception(f"Erro ao processar URL do convite: {str(e)}")

async def prepare_receive_invitation_payload(connection_alias: str, invitation_url: str) -> dict:
    try:
        invitation_data = await parse_invitation_url(invitation_url)
        
        payload = {
            "invitation": invitation_data,
            "auto_accept": True,
            "alias": connection_alias
        }
        
        print(f"Prepared receive-invitation payload: {payload}")
        return payload
    except Exception as e:
        print(f"Failed to prepare receive-invitation payload: {str(e)}")
        raise

async def receive_invitation(invitation_payload: dict) -> dict:
    try:
        result = await get_client().connection.receive_invitation(
            body=invitation_payload["invitation"],
            alias=invitation_payload.get("alias"),
            auto_accept=invitation_payload.get("auto_accept", True)
        )
        
        connection_info = result.to_dict() if hasattr(result, 'to_dict') else result
        
        print(f"Received invitation successfully: {connection_info}")
        return connection_info
        
    except Exception as e:
        print(f"Failed to receive invitation: {str(e)}")
        raise Exception(f"Erro ao aceitar convite: {str(e)}")
