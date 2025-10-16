from typing import List
from modules.client.service import AcaPyClient

def get_connections(alias: str = None, id: str = None) -> List[dict] | str:
    try:
        result = AcaPyClient.connection.get_connections(alias=alias, id=id)

        if result is None:
            return "NO_CONNECTIONS_FOUND"
        
        return result
    except Exception as e:
        return "CONNECTION_RETRIEVAL_FAILED"

def get_did_document(did: str) -> dict | str:
    try:
        did_info = AcaPyClient.did.get_did(did=did)
        if did_info is None:
            return "DID_NOT_FOUND"


        result = AcaPyClient.did.mount_document(did=did_info['did'], verkey=did_info['verkey'])

        if result is None:
            return "NO_DID_DOCUMENT_FOUND"
        
        return result
    except Exception as e:
        print(e)
        return "DID_DOCUMENT_RETRIEVAL_FAILED"