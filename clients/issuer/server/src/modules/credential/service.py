from typing import List
from modules.utils.ssi import get_client
from modules.credential.schema import CredentialDetail

async def create_schema(schema_name: str, schema_version: str, attributes: List[str]) -> dict | str:
        try:
            schema_body = {
                "schema_name": schema_name,
                "schema_version": schema_version,
                "attributes": attributes
            }
            result = await get_client().schema.publish_schema(body=schema_body)
            schema_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            return schema_data
        except Exception as e:
            return "SCHEMA_CREATION_FAILED"
        
async def create_credential_definition(schema_id: str, support_revocation: bool = False) -> dict | str:
        try:
            cred_def_body = {
                "schema_id": schema_id,
                "support_revocation": support_revocation
            }

            result = await get_client().credential_definition.publish_cred_def(body=cred_def_body)
            cred_def_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            return cred_def_data
        except Exception as e:
            return "CRED_DEF_CREATION_FAILED"
        
async def list_ledger_credentials() -> List[dict] | str:
    try:

        public_did = await get_client().wallet.get_public_did()
        did_info = public_did.to_dict() if hasattr(public_did, 'to_dict') else public_did

        result = await get_client().schema.get_created_schemas(schema_issuer_did=did_info['result']['did'])

        credentials = [cred.to_dict() if hasattr(cred, 'to_dict') else cred for cred in result]
        return credentials
    except Exception as e:
        return "CREDENTIAL_RETRIEVAL_FAILED"
    
async def get_credential_by_id(credential_id: str) -> dict | None:
    try:
        result = await get_client().schema.get_schema(schema_id=credential_id)
        credential = result.to_dict() if hasattr(result, 'to_dict') else result
        return CredentialDetail(
            id=credential['schema']['id'],
            name=credential['schema']['name'],
            version=credential['schema']['version'],
            attrNames=credential['schema']['attrNames']
        ) if credential else None
    except Exception as e:
        return None