from typing import List
from modules.webhook.schema import PresentProofRequest
from modules.client.service import AcaPyClient

def get_proof_requests() -> List[dict]:
    try:
        response = AcaPyClient.verify.get_proof_records(
            descending=False,
            limit=100,
            offset=0,
            order_by="id"
        )
        
        if not response or "results" not in response:
            return []
        
        proof_requests = []
        for record in response["results"]:
            by_format = record.get("by_format", {})
            pres_request = by_format.get("pres_request", {})
            indy_request = pres_request.get("indy", {}) if isinstance(pres_request, dict) else {}
            
            proof_request = {
                "pres_ex_id": record.get("pres_ex_id"),
                "state": record.get("state"),
                "name": indy_request.get("name"),
                "version": indy_request.get("version"),
                "requested_attributes": indy_request.get("requested_attributes", {}),
                "requested_predicates": indy_request.get("requested_predicates", {}),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at")
            }
            proof_requests.append(proof_request)
        
        return proof_requests
    except Exception as e:
        print(f"Erro ao buscar proof requests: {str(e)}")
        return []

def get_proof_request_by_id(pres_ex_id: str) -> dict | None:
    try:
        proof_request = PresentProofRequest.find_by_pres_ex_id(pres_ex_id)
        if proof_request:
            return proof_request.to_dict()
        return None
    except Exception as e:
        print(f"Erro ao buscar proof request: {str(e)}")
        return None

def get_credentials_for_proof_request(pres_ex_id: str) -> List[dict]:
    try:
        response = AcaPyClient.verify.get_credentials_for_proof_request(pres_ex_id)
        
        if not response:
            return []
        
        credentials = []
        for item in response:
            if 'cred_info' in item:
                cred_info = item['cred_info']
                transformed = {
                    'referent': cred_info.get('referent'),
                    'schema_id': cred_info.get('schema_id'),
                    'cred_def_id': cred_info.get('cred_def_id'),
                    'attrs': cred_info.get('attrs', {}),
                    'presentation_referents': item.get('presentation_referents', [])
                }
                credentials.append(transformed)
        
        return credentials
    except Exception as e:
        print(f"Erro ao buscar credenciais para proof request: {str(e)}")
        return []

def send_presentation(pres_ex_id: str, presentation_data: dict) -> dict | str:
    try:
        indy_data = presentation_data.get('indy', {})
        
        requested_attributes = {}
        for key, value in indy_data.get('requested_attributes', {}).items():
            requested_attributes[key] = {
                'cred_id': value.get('cred_id'),
                'revealed': value.get('revealed', True)
            }
        
        requested_predicates = {}
        for key, value in indy_data.get('requested_predicates', {}).items():
            requested_predicates[key] = {
                'cred_id': value.get('cred_id')
            }
        
        props = {
            'pres_ex_id': pres_ex_id,
            'requested_attributes': requested_attributes,
            'requested_predicates': requested_predicates,
            'self_attested_attributes': indy_data.get('self_attested_attributes', {}),
            'auto_remove': False
        }
        
        result = AcaPyClient.verify.send_presentation(props)
        
        if not result:
            return "PRESENTATION_SEND_FAILED"
        
        return result
    except Exception as e:
        print(f"Erro ao enviar apresentação: {str(e)}")
        return "PRESENTATION_SEND_FAILED"
