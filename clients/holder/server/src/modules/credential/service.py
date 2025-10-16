from typing import List
from modules.credential.schema import HolderCredentialRecord
from modules.client.service import AcaPyClient

def get_offers() -> List[dict]:
    offers = AcaPyClient.issue.get_offers()

    return offers

def accept_offer(cred_ex_id: str) -> dict | str:
    try:
        result = AcaPyClient.issue.send_request(cred_ex_id=cred_ex_id)
        return result
    except Exception as e:
        print(f"Erro ao aceitar a oferta de credencial: {str(e)}")
        return "OFFER_ACCEPTANCE_FAILED"

def get_holder_credentials() -> List[HolderCredentialRecord] | str:
    try:
        credentials = AcaPyClient.issue.get_stored_credentials()
        if not isinstance(credentials, list):
            credentials = [credentials]
        connections = AcaPyClient.connection.get_connections()
        if not isinstance(connections, list):
            connections = [connections]

        credentials_map = {}
        for cred in credentials:
            schema = cred.get("schema_id")
            schema_name = schema.split(":")[2] if schema else "unknown"
            schema_did = schema.split(":")[0] if schema else "unknown"

            if schema_did and schema_did not in credentials_map:
                credentials_map[schema_did] = cred

        connections_map = {}
        for conn in connections:
            public_did = conn.get("public_did")
            if public_did and public_did in credentials_map:
                connections_map[public_did] = conn

        credentials_result = []
        for schema_did, cred in credentials_map.items():
            conn = connections_map.get(schema_did)

            credentials_result.append({
                "issuer_did": schema_did,
                "issuer_name": conn.get("company_name") if conn else None,
                "connection_id": conn.get("connection_id") if conn else None,
                "schema_id": cred.get("schema_id"),
                "cred_def_id": cred.get("cred_def_id"),
                "attrs": cred.get("attrs"),
            })

        return credentials_result
    
    except Exception as e:
        print(f"Erro ao buscar credenciais do holder: {str(e)}")
        return "CREDENTIAL_RETRIEVAL_FAILED"
