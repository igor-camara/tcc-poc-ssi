from modules.webhook.schema import Notification, PresentProofRequest
from modules.client.service import AcaPyClient

def process_present_proof_v2_0(body: dict):
    try:
        if not 'state' in body:
            return None
        print(body)
        
        if body['state'] == 'request-sent':
            return create_proof_request_record(body)
        
        if body['state'] == 'presentation-received':
            return receive_proof_request(body)
        
        if body['state'] == 'abandoned':
            return update_proof_request_abandoned(body)
        
        if body['state'] == 'done':
            return update_proof_request_done(body)
        
        return None
        
    except Exception as e:
        print(f"Erro ao processar present proof v2.0: {str(e)}")
        raise e

def create_proof_request_record(body: dict):
    """Cria o registro do proof request quando o verifier envia a solicitação"""
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
    print(f"Proof request {pres_ex_id} criado com estado request-sent")
    
    return proof_request.to_dict()

def receive_proof_request(body: dict):
    try:
        pres_ex_id = body.get('pres_ex_id')
        
        if not pres_ex_id:
            print("Erro: pres_ex_id não encontrado no payload")
            return None
        
        print(f"Verificando apresentação para pres_ex_id: {pres_ex_id}")
        result = AcaPyClient.verify.verify_presentation(pres_ex_id)
        
        if result:
            print(f"Apresentação verificada com sucesso: {result}")
        else:
            print("Falha ao verificar apresentação")
        
        return result
    except Exception as e:
        print(f"Erro ao processar receive_proof_request: {str(e)}")
        raise e

def update_proof_request_abandoned(body: dict):
    """Atualiza proof request com estado abandoned e mensagem de erro"""
    pres_ex_id = body.get('pres_ex_id')
    
    if not pres_ex_id:
        print("Erro: pres_ex_id não encontrado no payload")
        return None
    
    # Busca o proof request existente
    proof_request = PresentProofRequest.find_by_pres_ex_id(pres_ex_id)
    
    if proof_request:
        # Atualiza com o estado abandoned
        proof_request.state = body.get('state')
        # Como não recebemos error_msg do holder, indicamos apenas que houve erro
        proof_request.error_msg = "O holder não conseguiu gerar a apresentação"
        proof_request.updated_at = body.get('updated_at')
        proof_request.save()
        
        print(f"Proof request {pres_ex_id} marcado como abandoned")
        
        # Cria notificação de erro para o verifier
        notification = Notification(
            tipo="proof-presentation-abandoned",
            connection_id=body.get('connection_id'),
        )
        notification.save()
        
        return proof_request.to_dict()
    else:
        print(f"Proof request {pres_ex_id} não encontrado para atualizar")
        return None

def update_proof_request_done(body: dict):
    """Atualiza proof request com estado done e resultado da verificação"""
    pres_ex_id = body.get('pres_ex_id')
    
    if not pres_ex_id:
        print("Erro: pres_ex_id não encontrado no payload")
        return None
    
    # Busca o proof request existente
    proof_request = PresentProofRequest.find_by_pres_ex_id(pres_ex_id)
    
    if proof_request:
        # Atualiza com o estado done e resultado da verificação
        proof_request.state = body.get('state')
        proof_request.verified = body.get('verified', 'N/A')
        proof_request.updated_at = body.get('updated_at')
        proof_request.save()
        
        print(f"Proof request {pres_ex_id} marcado como done. Verified: {proof_request.verified}")
        return proof_request.to_dict()
    else:
        print(f"Proof request {pres_ex_id} não encontrado para atualizar")
        return None
