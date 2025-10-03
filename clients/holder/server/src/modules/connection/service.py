from typing import List
from modules.invitation.service import get_client
from modules.connection.schema import (
    ConnectionResponse, 
    DIDDocumentResponse, 
    VerificationMethod, 
    Service
)

async def get_connections(alias: str = None, state: str = None) -> List[dict] | str:
    try:
        result = await get_client().connection.get_connections(
            alias=alias,
            state=state
        )
        connections = result.to_dict() if hasattr(result, 'to_dict') else result
        if isinstance(connections, dict) and 'results' in connections:
            connections_list = []
            for conn in connections['results']:
                connections_list.append(
                    ConnectionResponse(
                        alias=conn.get('alias', ''),
                        connection_id=conn.get('connection_id', ''),
                        created_at=conn.get('created_at', ''),
                        invitation_key=conn.get('invitation_key', ''),
                        invitation_mode=conn.get('invitation_mode', ''),
                        state=conn.get('state', '')
                    )
                )
            return connections_list
        return []
    except Exception as e:
        return "CONNECTION_RETRIEVAL_FAILED"

async def get_did_document(did: str) -> DIDDocumentResponse | str:
    """
    Monta o DID Document para um DID específico.
    
    O DID Document é um documento estruturado que contém informações sobre:
    - Métodos de verificação (chaves públicas)
    - Métodos de autenticação
    - Serviços associados ao DID
    
    Args:
        did: O DID (Decentralized Identifier) a ser consultado
        
    Returns:
        DIDDocumentResponse ou código de erro como string
    """
    try:
        # Busca o DID na wallet
        result = await get_client().wallet.get_did_endpoint(did=did)
        did_result = result.to_dict() if hasattr(result, 'to_dict') else result
        
        # Extrai informações do DID
        verkey = did_result.get('verkey')
        endpoint = did_result.get('endpoint', '')
        
        # Se não encontrou o DID na wallet, tenta buscar informações do ledger
        if not verkey:
            try:
                ledger_result = await get_client().ledger.get_did_verkey(did=did)
                ledger_data = ledger_result.to_dict() if hasattr(ledger_result, 'to_dict') else ledger_result
                verkey = ledger_data.get('verkey')
            except Exception:
                return "DID_NOT_FOUND"
        
        # Monta o DID Document seguindo o padrão W3C DID Core
        verification_method_id = f"{did}#key-1"
        
        verification_methods = [
            VerificationMethod(
                id=verification_method_id,
                type="Ed25519VerificationKey2018",
                controller=did,
                publicKeyBase58=verkey
            )
        ]
        
        # Lista de referências para métodos de autenticação
        authentication = [verification_method_id]
        
        # Monta serviços se houver endpoint
        services = []
        if endpoint:
            services.append(
                Service(
                    id=f"{did}#did-communication",
                    type="did-communication",
                    serviceEndpoint=endpoint,
                    recipientKeys=[verkey],
                    routingKeys=[]
                )
            )
        
        # Cria o DID Document
        did_document = DIDDocumentResponse(
            context=[
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2018/v1"
            ],
            id=did,
            verificationMethod=verification_methods,
            authentication=authentication,
            assertionMethod=[verification_method_id],
            service=services if services else None
        )
        
        return did_document
        
    except Exception as e:
        print(f"Error getting DID document: {str(e)}")
        return "DID_DOCUMENT_RETRIEVAL_FAILED"