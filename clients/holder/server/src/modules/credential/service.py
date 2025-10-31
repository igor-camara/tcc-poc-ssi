from typing import List
from modules.credential.schema import HolderCredentialRecord
from modules.client.service import AcaPyClient
from modules.user.schema import User

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

def get_holder_credentials(did: str) -> List[HolderCredentialRecord] | str:
    try:
        user_dids = User.get_ephemeral_dids_by_user_did(did)
        if not user_dids:
            return []

        credentials = AcaPyClient.issue.get_stored_credentials()
        if not credentials:
            return []
        if not isinstance(credentials, list):
            credentials = [credentials]
        connections = AcaPyClient.connection.get_connections()
        if not isinstance(connections, list):
            connections = [connections]

        credentials_map = {}
        for cred in credentials:
            schema = cred.get("schema_id")

            if schema not in credentials_map:
                credentials_map[schema] = cred
        
        connections_map = {}
        for conn in connections:
            their_public_did = conn.get("their_public_did")
            my_did = conn.get("my_did")

            if my_did in [ud['ephemeral_did'] for ud in user_dids]:
                connections_map[their_public_did] = conn

        credentials_result = []
        for schema, cred in credentials_map.items():
            issuer_did = schema.split(":")[0]
            conn = connections_map.get(issuer_did)


            credentials_result.append({
                "issuer_did": issuer_did,
                "issuer_name": conn.get("their_label"),
                "schema_id": cred.get("schema_id"),
                "cred_def_id": cred.get("cred_def_id"),
                "attrs": cred.get("attrs"),
            })

        return credentials_result
    
    except Exception as e:
        print(f"Erro ao buscar credenciais do holder: {str(e)}")
        return "CREDENTIAL_RETRIEVAL_FAILED"
