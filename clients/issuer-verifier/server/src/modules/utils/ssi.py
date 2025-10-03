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
        return "DID_CREATION_FAILED"

async def register_did_on_ledger(did, verkey, alias=None) -> bool:
    try:
        result = await get_client().ledger.register_nym(
            did=did,
            verkey=verkey,
            alias=alias,
            role=None
        )
        
        return True
    except Exception as e:
        return False
