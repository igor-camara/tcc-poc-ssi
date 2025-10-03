from typing import List, Dict, Any, Optional
from modules.utils.ssi import get_client
from modules.credential.schema import CredentialDetail, IssuedCredentialRecord

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
        
async def get_connection_by_id(connection_id: str) -> dict | None:
    try:
        result = await get_client().connection.get_connection(connection_id=connection_id)
        connection = result.to_dict() if hasattr(result, 'to_dict') else result
        return connection
    except Exception as e:
        return None
        
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

async def get_credential_definition_by_id(cred_def_id: str) -> dict | None:
    """
    Get credential definition by ID
    """
    try:
        result = await get_client().credential_definition.get_cred_def(cred_def_id=cred_def_id)
        cred_def = result.to_dict() if hasattr(result, 'to_dict') else result
        return cred_def
    except Exception as e:
        return None

async def send_credential_offer(
    connection_id: str,
    cred_def_id: str,
    attributes: Dict[str, Any],
    comment: str = ""
) -> dict | str:
    """
    Send a credential offer to a holder via an established connection
    """
    try:
        # Prepare credential attributes in the format expected by ACA-Py
        credential_preview_attributes = [
            {"name": key, "value": str(value)}
            for key, value in attributes.items()
        ]
        
        offer_body = {
            "auto_issue": False,
            "auto_remove": False,
            "comment": comment,
            "connection_id": connection_id,
            "credential_preview": {
                "@type": "https://didcomm.org/issue-credential/2.0/credential-preview",
                "attributes": credential_preview_attributes
            },
            "filter": {
                "indy": {
                    "cred_def_id": cred_def_id
                }
            },
            "trace": False
        }
        
        result = await get_client().issue_credential_v2_0.send_offer(body=offer_body)
        offer_data = result.to_dict() if hasattr(result, 'to_dict') else result
        
        return offer_data
    except Exception as e:
        return "CREDENTIAL_OFFER_FAILED"

async def get_issued_credentials() -> List[IssuedCredentialRecord] | str:
    """
    Get all issued credentials with their status
    Returns a compiled list with the most important information for frontend display
    """
    try:
        # Get all credential exchange records
        result = await get_client().issue_credential_v2_0.get_records()
        records = result.to_dict() if hasattr(result, 'to_dict') else result
        
        issued_credentials = []
        
        # Process each credential exchange record
        for record in records.get('results', []):
            # Get credential definition details to extract schema information
            cred_def_id = None
            credential_name = "Unknown Credential"
            
            # Extract credential definition ID from the record
            if record.get('cred_ex_record'):
                cred_ex = record['cred_ex_record']
                if cred_ex.get('by_format', {}).get('cred_offer', {}).get('indy'):
                    cred_def_id = cred_ex['by_format']['cred_offer']['indy'].get('cred_def_id')
            
            # Try to get schema name from credential definition
            if cred_def_id:
                try:
                    cred_def = await get_credential_definition_by_id(cred_def_id)
                    if cred_def and cred_def.get('credential_definition'):
                        schema_id = cred_def['credential_definition'].get('schemaId', '')
                        # Extract schema name from schema_id (format: did:indy:network:did/anoncreds/v0/SCHEMA/name/version)
                        if '/SCHEMA/' in schema_id:
                            parts = schema_id.split('/SCHEMA/')
                            if len(parts) > 1:
                                name_version = parts[1].split('/')
                                if len(name_version) >= 1:
                                    credential_name = name_version[0]
                except:
                    pass
            
            # Get connection details to extract holder information
            connection_id = record.get('cred_ex_record', {}).get('connection_id')
            holder_did = None
            holder_alias = None
            
            if connection_id:
                try:
                    connection = await get_connection_by_id(connection_id)
                    if connection:
                        holder_did = connection.get('their_did')
                        holder_alias = connection.get('alias') or connection.get('their_label')
                except:
                    pass
            
            # Extract credential attributes
            attributes = None
            if record.get('cred_ex_record', {}).get('by_format', {}).get('cred_offer', {}).get('indy', {}).get('credential_preview'):
                attrs = record['cred_ex_record']['by_format']['cred_offer']['indy']['credential_preview'].get('attributes', [])
                attributes = {attr['name']: attr['value'] for attr in attrs}
            
            # Get issued timestamp (use updated_at or created_at)
            issued_at = record.get('cred_ex_record', {}).get('updated_at') or record.get('cred_ex_record', {}).get('created_at')
            
            # Get status
            status = record.get('cred_ex_record', {}).get('state', 'unknown')
            
            issued_credential = IssuedCredentialRecord(
                credential_exchange_id=record.get('cred_ex_record', {}).get('cred_ex_id', 'unknown'),
                credential_name=credential_name,
                credential_definition_id=cred_def_id or 'unknown',
                issued_at=issued_at,
                holder_did=holder_did,
                holder_alias=holder_alias,
                status=status,
                attributes=attributes
            )
            
            issued_credentials.append(issued_credential)
        
        return issued_credentials
    except Exception as e:
        return f"ISSUED_CREDENTIALS_RETRIEVAL_FAILED: {str(e)}"