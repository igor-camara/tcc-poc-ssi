from modules.webhook.schema import Notification, PresentProofRequest, CredentialOffer
from modules.client.service import AcaPyClient
import json

def process_issue_credential_v2_0(body: dict):
    try:
        if not 'state' in body:
            return None
        
        if body['state'] == 'offer-received':
            return receive_offer(body)
        if body['state'] == 'credential-received':
            print("Storing received credential...")
            return store_credential(body)
        
        return None
        
    except Exception as e:
        print(f"Erro ao processar issue credential v2.0: {str(e)}")
        raise e
    
def receive_offer(body: dict):
    # Extrai identificadores da credencial
    schema_id = None
    cred_def_id = None
    credential_preview = []
    
    if 'by_format' in body:
        by_format = body.get('by_format', {})
        
        if 'cred_offer' in by_format:
            indy_offer = by_format['cred_offer'].get('indy', {})
            schema_id = indy_offer.get('schema_id')
            cred_def_id = indy_offer.get('cred_def_id')
        
        if not schema_id and 'cred_proposal' in by_format:
            indy_proposal = by_format['cred_proposal'].get('indy', {})
            schema_id = indy_proposal.get('schema_id')
            cred_def_id = indy_proposal.get('cred_def_id')
        
        if not schema_id and 'cred_issue' in by_format:
            indy_issue = by_format['cred_issue'].get('indy', {})
    
    # Extrai o preview do payload
    if 'payload' in body and body['payload']:
        try:
            payload = body['payload']
            if isinstance(payload, str):
                payload = json.loads(payload)
            
            if 'credential_preview' in payload:
                cred_preview = payload['credential_preview']
                if 'attributes' in cred_preview:
                    credential_preview = cred_preview['attributes']
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao extrair credential_preview do payload: {str(e)}")
    
    # Salva oferta da credencial (com dados para preview)
    cred_ex_id = body.get('cred_ex_id')
    if cred_ex_id:
        credential_offer = CredentialOffer(
            cred_ex_id=cred_ex_id,
            connection_id=body.get('connection_id'),
            state=body.get('state'),
            credential_preview=credential_preview,
            schema_id=schema_id,
            cred_def_id=cred_def_id
        )
        credential_offer.save()

    return None

def store_credential(body: dict):
    cred_ex_id = body.get('cred_ex_id')

    result = AcaPyClient.issue.store_credential(cred_ex_id)

    notification = Notification(
        tipo="credential-received",
        connection_id=body.get('connection_id'),
    )
    
    notification.save()

    return None

def process_present_proof_v2_0(body: dict):
    try:
        if not 'state' in body:
            return None
        
        if body['state'] == 'request-received':
            return receive_proof_request(body)
        
        return None
        
    except Exception as e:
        print(f"Erro ao processar present proof v2.0: {str(e)}")
        raise e

def receive_proof_request(body: dict):
    pres_ex_id = body.get('pres_ex_id')
    state = body.get('state')
    
    by_format = body.get('by_format', {})
    pres_request = by_format.get('pres_request', {})
    indy_request = pres_request.get('indy', {})
    
    name = indy_request.get('name')
    version = indy_request.get('version')
    requested_attributes = indy_request.get('requested_attributes', {})
    requested_predicates = indy_request.get('requested_predicates', {})
    
    created_at = body.get('created_at')
    updated_at = body.get('updated_at')
    
    proof_request = PresentProofRequest(
        pres_ex_id=pres_ex_id,
        state=state,
        name=name,
        version=version,
        requested_attributes=requested_attributes,
        requested_predicates=requested_predicates,
        created_at=created_at,
        updated_at=updated_at
    )
    
    proof_request.save()
    
    notification = Notification(
        tipo="proof-request-received",
        connection_id=body.get('connection_id'),
    )
    
    notification.save()
    
    return proof_request.to_dict()
