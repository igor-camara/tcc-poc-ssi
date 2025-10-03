from typing import List
from modules.utils.ssi import get_client

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