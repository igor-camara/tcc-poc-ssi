from typing import List, Dict, Any
from modules.utils.ssi import get_client
from modules.credential.schema import CredentialDetail, IssuedCredentialRecord
from modules.client.service import AcaPyClient

def create_schema(schema_name: str, schema_version: str, attributes: List[str]) -> dict | str:
    try:
        return AcaPyClient.schemas.create_schema(schema_name=schema_name, schema_version=schema_version, attributes=attributes)
    except Exception as e:
        print(e)
        return "SCHEMA_CREATION_FAILED"
        
def get_connection_by_id(connection_id: str) -> dict | None:
    try:
        return AcaPyClient.connection.get_connections(id=connection_id)
    except Exception as e:
        print(e)
        return None
        
def create_credential_definition(schema_id: str, support_revocation: bool = False) -> dict | str:
    try:
        return AcaPyClient.schemas.create_cred_def(schema_id=schema_id, support_revocation=support_revocation)
    except Exception as e:
        print(e)
        return "CRED_DEF_CREATION_FAILED"
        
def list_ledger_credentials() -> List[dict] | str:
    try:
        schema_ids_response = AcaPyClient.schemas.get_schemas_id()
        
        if not schema_ids_response:
            return []

        schemas = []
        for schema_id in schema_ids_response.get('schema_ids', []):
            schema = AcaPyClient.schemas.get_schema(id=schema_id)
            if not schema:
                continue
        
            schema_data = {
                "id": schema["id"],
                "name": schema["name"],
                "version": schema["version"],
                "attributes": schema["attrNames"],
                "seqNo": schema["seqNo"]
            }
            schemas.append(schema_data)

        return schemas
    except Exception as e:
        print(f"Error listing ledger credentials: {e}")
        return "CREDENTIAL_RETRIEVAL_FAILED"
    
def get_credential_by_id(credential_id: str) -> CredentialDetail | None:
    try:
        return AcaPyClient.schemas.get_schema(id=credential_id)
    except Exception as e:
        print(e)
        return None

def get_credential_definition_by_schema_id(schema_id: str) -> dict | None:
    try:
        result = AcaPyClient.schemas.get_cred_defs_id(schema_id=schema_id)
        if not result or 'credential_definition_ids' not in result:
            return None

        creds = []
        for cred_def_id in result['credential_definition_ids']:
            cred_def = AcaPyClient.schemas.get_cred_def(id=cred_def_id)
            if cred_def:
                creds.append(cred_def)
        return creds
    except Exception as e:
        print(e)
        return None

def send_credential_offer(connection_id: str, cred_def_id: str, schema_id: str, attributes: list[dict]) -> dict | str:
    try:
        return AcaPyClient.issue.send_offer(props={
            "auto_issue": False,
            "auto_remove": True,
            "connection_id": connection_id,
            "cred_def_id": cred_def_id,
            "issuer_did": AcaPyClient.did.get_public_did()['did'],
            "schema_id": schema_id,
            "attributes": attributes
        })
    except Exception as e:
        print(e)
        return "CREDENTIAL_OFFER_FAILED"

def get_issued_credentials() -> List[IssuedCredentialRecord] | str:
    try:
        records = AcaPyClient.issue.get_offers()
        
        if not records:
            return []
        
        # Handle case where _fields returns a single dict instead of a list
        if isinstance(records, dict):
            records = [records]
        elif not isinstance(records, list):
            return []
        
        issued_credentials = []
        
        for record in records:
            # Get connection details to fetch holder alias
            connection_id = record.get('connection_id')
            connection = None
            holder_alias = None
            
            if connection_id:
                connection = get_connection_by_id(connection_id)
                if connection and isinstance(connection, dict):
                    holder_alias = connection.get('their_label') or connection.get('alias')
            
            # Extract credential attributes from the credential preview
            attributes = {}
            cred_preview = record.get('cred_preview')
            if cred_preview:
                attrs_list = cred_preview.get('attributes', [])
                for attr in attrs_list:
                    if isinstance(attr, dict) and 'name' in attr and 'value' in attr:
                        attributes[attr['name']] = attr['value']
            
            # Extract schema information from filter or directly from record
            cred_filter = record.get('filter', {})
            indy_filter = cred_filter.get('indy', {}) if isinstance(cred_filter, dict) else {}
            
            # Try to get from filter first, then fall back to record root
            schema_id = indy_filter.get('schema_id', '') or record.get('schema_id', '')
            cred_def_id = indy_filter.get('cred_def_id', '') or record.get('cred_def_id', '')
            
            # Extract credential name - try schema_name field first, then parse from schema_id
            credential_name = indy_filter.get('schema_name', '') or record.get('schema_name', '')
            
            if not credential_name and schema_id:
                # Parse from schema_id format: issuer_did:2:schema_name:version
                parts = schema_id.split(':')
                if len(parts) >= 3:
                    credential_name = parts[2]  # Schema name is at index 2
            
            # Extract holder DID from connection or credential
            holder_did = None
            if connection and isinstance(connection, dict):
                holder_did = connection.get('their_did')
            
            issued_credential = IssuedCredentialRecord(
                credential_exchange_id=record.get('cred_ex_id', ''),
                credential_name=credential_name,
                credential_definition_id=cred_def_id,
                issued_at=record.get('created_at'),
                holder_did=holder_did,
                holder_alias=holder_alias,
                status=record.get('state', ''),
                attributes=attributes if attributes else None
            )
            
            issued_credentials.append(issued_credential)
        
        return issued_credentials

    except Exception as e:
        return f"ISSUED_CREDENTIALS_RETRIEVAL_FAILED: {str(e)}"
    
def issue_credential(cred_ex_id: str) -> dict | str:
    try:
        return AcaPyClient.issue.issue_credential(cred_ex_id=cred_ex_id)
    except Exception as e:
        print(e)
        return "CREDENTIAL_ISSUANCE_FAILED"