from typing import List
from modules.invitation.service import get_client
from modules.credential.schema import HolderCredentialRecord

async def get_holder_credentials() -> List[HolderCredentialRecord] | str:
    """
    Busca todas as credenciais que o Holder possui.
    Retorna uma lista com informações compiladas sobre cada credencial:
    - Quem emitiu (emissor)
    - Quando foi emitida
    - Nome/Descrição da credencial
    - Detalhes (atributos, versão)
    - Status da credencial
    """
    try:
        # Busca todos os registros de troca de credenciais
        result = await get_client().issue_credential_v2_0.get_records()
        records = result.to_dict() if hasattr(result, 'to_dict') else result
        
        holder_credentials = []
        
        # Processa cada registro de troca de credencial
        for record in records.get('results', []):
            # Extrai informações básicas do registro
            cred_ex_id = record.get('cred_ex_id', '')
            state = record.get('state', '')
            created_at = record.get('created_at', '')
            updated_at = record.get('updated_at', '')
            
            # Inicializa variáveis
            credential_name = "Credencial Desconhecida"
            cred_def_id = None
            schema_id = None
            issuer_did = None
            credential_id = None
            attributes = {}
            version = None
            
            # Extrai informações da credencial
            cred_ex_record = record.get('cred_ex_record', {})
            
            # Busca credential_id se a credencial foi emitida
            if cred_ex_record.get('cred_id_stored'):
                credential_id = cred_ex_record.get('cred_id_stored')
            
            # Extrai informações do formato Indy
            by_format = cred_ex_record.get('by_format', {})
            
            # Tenta extrair do credential offer
            if by_format.get('cred_offer', {}).get('indy'):
                indy_offer = by_format['cred_offer']['indy']
                cred_def_id = indy_offer.get('cred_def_id')
                schema_id = indy_offer.get('schema_id')
            
            # Tenta extrair do credential issue (quando já foi emitida)
            if by_format.get('cred_issue', {}).get('indy'):
                indy_issue = by_format['cred_issue']['indy']
                if not cred_def_id:
                    cred_def_id = indy_issue.get('cred_def_id')
                if not schema_id:
                    schema_id = indy_issue.get('schema_id')
            
            # Tenta extrair do credential (quando armazenada)
            if by_format.get('cred', {}).get('indy'):
                indy_cred = by_format['cred']['indy']
                if not cred_def_id:
                    cred_def_id = indy_cred.get('cred_def_id')
                if not schema_id:
                    schema_id = indy_cred.get('schema_id')
            
            # Extrai atributos da credencial preview ou da credencial emitida
            cred_preview = cred_ex_record.get('cred_preview', {})
            if cred_preview and cred_preview.get('attributes'):
                attributes = {
                    attr['name']: attr['value'] 
                    for attr in cred_preview['attributes']
                }
            
            # Se temos credential_id, podemos buscar a credencial armazenada para mais detalhes
            if credential_id:
                try:
                    stored_cred = await get_client().credentials.get_record(credential_id=credential_id)
                    stored_cred_dict = stored_cred.to_dict() if hasattr(stored_cred, 'to_dict') else stored_cred
                    
                    # Extrai atributos se disponíveis
                    if stored_cred_dict.get('attrs'):
                        attributes = stored_cred_dict['attrs']
                    
                    if not schema_id:
                        schema_id = stored_cred_dict.get('schema_id')
                    if not cred_def_id:
                        cred_def_id = stored_cred_dict.get('cred_def_id')
                except Exception as e:
                    # Se falhar, continua com as informações que já temos
                    pass
            
            # Extrai nome e versão do schema_id
            if schema_id:
                # Formato: did:indy:network:did/anoncreds/v0/SCHEMA/name/version
                # ou outro formato dependendo da rede
                if '/SCHEMA/' in schema_id:
                    parts = schema_id.split('/SCHEMA/')
                    if len(parts) > 1:
                        schema_parts = parts[1].split('/')
                        if len(schema_parts) >= 2:
                            credential_name = schema_parts[0].replace('-', ' ').title()
                            version = schema_parts[1]
                elif ':' in schema_id:
                    # Formato alternativo: issuer_did:2:name:version
                    schema_parts = schema_id.split(':')
                    if len(schema_parts) >= 4:
                        credential_name = schema_parts[2].replace('-', ' ').title()
                        version = schema_parts[3]
            
            # Extrai issuer DID do cred_def_id ou schema_id
            if cred_def_id:
                # Formato: did:indy:network:issuer_did/anoncreds/v0/CLAIM_DEF/...
                if 'did:indy:' in cred_def_id:
                    parts = cred_def_id.split('/')
                    if len(parts) > 0:
                        issuer_did = parts[0].split('did:indy:')[-1]
                elif ':' in cred_def_id:
                    # Formato alternativo: issuer_did:3:CL:schema_seq_no:tag
                    issuer_did = cred_def_id.split(':')[0]
            
            # Busca informações da conexão para obter alias do emissor
            connection_id = record.get('connection_id')
            issuer_alias = None
            if connection_id:
                try:
                    connection = await get_client().connection.get_connection(connection_id=connection_id)
                    conn_dict = connection.to_dict() if hasattr(connection, 'to_dict') else connection
                    issuer_alias = conn_dict.get('their_label') or conn_dict.get('alias')
                except Exception as e:
                    # Se falhar, usa o DID como fallback
                    pass
            
            # Determina se a credencial é válida baseado no status
            is_valid = state in ['credential-issued', 'done', 'credential-received']
            
            # Cria o registro da credencial
            credential_record = HolderCredentialRecord(
                credential_exchange_id=cred_ex_id,
                credential_id=credential_id,
                credential_name=credential_name,
                credential_definition_id=cred_def_id or "N/A",
                schema_id=schema_id,
                issuer_did=issuer_did,
                issuer_alias=issuer_alias,
                issued_at=created_at,
                received_at=updated_at,
                status=state,
                attributes=attributes if attributes else None,
                version=version,
                is_valid=is_valid
            )
            
            holder_credentials.append(credential_record)
        
        return holder_credentials
    
    except Exception as e:
        print(f"Erro ao buscar credenciais do holder: {str(e)}")
        return "CREDENTIAL_RETRIEVAL_FAILED"
