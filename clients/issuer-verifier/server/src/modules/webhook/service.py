from modules.webhook.schema import Notification, PresentProofRequest
from modules.client.service import AcaPyClient

def process_present_proof_v2_0(body: dict):
    try:
        if not 'state' in body:
            return None
        print(body)
        if body['state'] == 'presentation-received':
            return receive_proof_request(body)
        
        return None
        
    except Exception as e:
        print(f"Erro ao processar present proof v2.0: {str(e)}")
        raise e

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
