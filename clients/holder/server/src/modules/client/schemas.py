import httpx
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class Base:
    @staticmethod
    def _fields(body: dict, fields: list, result: dict = None):
        if result is None:
            result = {}
        
        list_keys = ["results", "records", "connections", "credentials", "items"]
        for list_key in list_keys:
            if list_key in body and isinstance(body[list_key], list):
                results_list = []
                for item in body[list_key]:
                    if isinstance(item, dict):
                        item_result = {}
                        Base._fields(item, fields, item_result)
                        results_list.append(item_result)
                return results_list if len(results_list) > 1 else (results_list[0] if results_list else {})
        
        for key, value in body.items():
            if key in fields:
                result[key] = value
                continue

            if isinstance(value, dict):
                Base._fields(value, fields, result)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        Base._fields(item, fields, result)            
        return result

class ClientDid(Base):
    def __init__(self, url: str):
        self.url = url
        logging.info(f"ClientDid inicializado com URL base: {self.url}")

    def create(self, method: str = "sov", key_type: str = "ed25519"):
        endpoint = f"{self.url}/wallet/did/create"
        body = {
            "method": method,
            "options": {
                "key_type": key_type
            }
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"DID criado com sucesso.")
                return self._fields(response.json(), ["did", "verkey", "method"])
            else:
                logging.error(f"Falha ao criar DID. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def register_on_ledger(self, did: str, verkey: str, method: str, alias: str):
        endpoint = f"{self.url}/ledger/register-nym"
        params = {
            "did": f"did:{method}:{did}",
            "verkey": verkey,
            "alias": alias
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, params=params, timeout=10.0)

            if response.status_code == 200:
                result = self._fields(response.json(), ["success", "created_at", "state"])
                if result.get("success"):
                    logging.info(f"DID {did} registrado com sucesso na ledger.")
                else:
                    logging.warning(f"DID {did} não pôde ser registrado na ledger.")
                return result
            else:
                logging.error(f"Falha ao registrar DID no ledger. Corpo da resposta: {response.text}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_public_did(self):
        endpoint = f"{self.url}/wallet/did/public"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"DID público obtido com sucesso.")
                return self._fields(response.json(), ["did", "verkey", "method"])
            else:
                logging.error(f"Falha ao obter DID público. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_did(self, did: str):
        endpoint = f"{self.url}/wallet/did"
        params = {
            "did": did
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, params=params, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"DID obtido com sucesso.")
                return self._fields(response.json(), ["did", "verkey", "method"])
            else:
                logging.error(f"Falha ao obter DID. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    @staticmethod
    def mount_document(did: str, verkey: str):
        return {
            "@context": [
                "https://www.w3.org/ns/did/v1"
            ],
            "id": did,
            "verificationMethod": [
                {
                    "id": f"{did}#key-1",
                    "type": "Ed25519VerificationKey2018",
                    "controller": did,
                    "publicKeyBase58": verkey
                }
            ],
            "authentication": [
                f"{did}#key-1"
            ],
            "assertionMethod": [
                f"{did}#key-1"
            ]
        }

class ClientConnection(Base):
    def __init__(self, url: str):
        self.url = url
        logging.info(f"ClientConnection inicializado com URL base: {self.url}")

    def create(self, alias: str, label: str):
        endpoint = f"{self.url}/out-of-band/create-invitation"
        body = {
            "alias": alias,
            "accept": [
                "didcomm/aip1",
                "didcomm/aip2;env=rfc19"
            ],
            "handshake_protocols": [
                "https://didcomm.org/didexchange/1.0"
            ],
            "my_label": label,
            "protocol_version": "1.1"
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Convite criado com sucesso.")
                return self._fields(response.json(), ["label", "@id", "invitation_url", "created_at", "state"])
            else:
                logging.error(f"Falha ao criar convite. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def receive(self, invitation_url: dict):
        endpoint = f"{self.url}/out-of-band/receive-invitation"
        body = self._from_oob(invitation_url)

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Convite recebido com sucesso.")
                return self._fields(response.json(), ["@id", "label"])
            else:
                logging.error(f"Falha ao receber convite. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_connections(self, id: str = None, alias : str = None):
        endpoint = f"{self.url}/connections"
        params = {}
        if alias and id:
            return None
        if alias:
            params["alias"] = alias
        if id:
            endpoint += f"/{id}"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            if params:
                response = httpx.get(endpoint, params=params, timeout=10.0)
            else:
                response = httpx.get(endpoint, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Conexões obtidas com sucesso.")
                return self._fields(response.json(), ["state", "created_at", "updated_at", "connection_id", "my_did", "their_did", "their_label", "invitation_key", "alias", "company_name", "public_did"])
            else:
                logging.error(f"Falha ao obter conexões. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    @staticmethod
    def _from_oob(url: str):
        if "oob=" in url:
            import urllib.parse
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            oob_param = query_params.get("oob", [None])[0]
            if oob_param:
                import base64
                import json
                try:
                    decoded_bytes = base64.urlsafe_b64decode(oob_param + '==')
                    decoded_str = decoded_bytes.decode('utf-8')
                    invitation = json.loads(decoded_str)
                    return invitation
                except (base64.binascii.Error, json.JSONDecodeError) as e:
                    logging.error(f"Erro ao decodificar o parâmetro oob: {e}")
                    return None
        logging.error("Parâmetro 'oob' não encontrado na URL.")
        return None

class ClientSchemas(Base):
    def __init__(self, url: str):
        self.url = url
        logging.info(f"ClientSchemas inicializado com URL base: {self.url}")

    def create_schema(self, schema_name: str, schema_version: str, attributes: list):
        endpoint = f"{self.url}/schemas"
        body = {
            "schema_name": schema_name,
            "schema_version": schema_version,
            "attributes": attributes
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Esquema criado com sucesso.")
                return self._fields(response.json(), ["schema_id", "state", "created_at"])
            else:
                logging.error(f"Falha ao criar esquema. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_schemas_id(self):
        endpoint = f"{self.url}/schemas/created"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Esquemas obtidos com sucesso.")
                return self._fields(response.json(), ["schema_ids"])
            else:
                logging.error(f"Falha ao obter esquemas. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_schema(self, id: str):
        endpoint = f"{self.url}/schemas/{id}"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Esquema obtido com sucesso.")
                return self._fields(response.json(), ["id", "name", "version", "attrNames", "seqNo"])
            else:
                logging.error(f"Falha ao obter esquema. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def create_cred_def(self, schema_id: str, support_revocation: bool = False):
        endpoint = f"{self.url}/credential-definitions"
        body = {
            "schema_id": schema_id,
            "support_revocation": support_revocation
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=30.0)

            if response.status_code == 200:
                logging.info(f"Definição de credencial criada com sucesso.")
                return self._fields(response.json(), ["credential_definition_id", "state", "created_at", "updated_at"])
            else:
                logging.error(f"Falha ao criar definição de credencial. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_cred_defs_id(self, schema_id: str = None):
        endpoint = f"{self.url}/credential-definitions/created"
        params = {}
        if schema_id:
            params["schema_id"] = schema_id

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            if params:
                response = httpx.get(endpoint, params=params, timeout=10.0)
            else:
                response = httpx.get(endpoint, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Definições de credenciais obtidas com sucesso.")
                return self._fields(response.json(), ["credential_definition_ids"])
            else:
                logging.error(f"Falha ao obter definições de credenciais. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_cred_def(self, id: str):
        endpoint = f"{self.url}/credential-definitions/{id}"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Definição de credencial obtida com sucesso.")
                return self._fields(response.json(), ["id", "schemaId"])
            else:
                logging.error(f"Falha ao obter definição de credencial. Corpo da resposta: {response.text}")
                return None

        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
class ClientIssue(Base):
    def __init__(self, url: str):
        self.url = url
        logging.info(f"ClientIssue inicializado com URL base: {self.url}")

    def send_offer(self, props: dict):
        if "auto_issue" not in props:
            props["auto_issue"] = True
        if "auto_remove" not in props:
            props["auto_remove"] = True

        if "connection_id" not in props:
            logging.error("Parâmetro obrigatório ausente: 'connection_id'")
            return None
        if "cred_def_id" not in props:
            logging.error("Parâmetro obrigatório ausente: 'cred_def_id'")
            return None    
        #if "credential_preview" not in props:
        #    logging.error("Parâmetro obrigatório ausente: 'credential_preview'")
        #    return None
        if "issuer_did" not in props:
            logging.error("Parâmetro obrigatório ausente: 'issuer_did'")
            return None
        if "schema_id" not in props:
            logging.error("Parâmetro obrigatório ausente: 'schema_id'")
            return None
        
        endpoint = f"{self.url}/issue-credential-2.0/send-offer"
        body = {
            "auto_issue": props["auto_issue"],
            "auto_remove": props["auto_remove"],
            "connection_id": props["connection_id"],
            "credential_preview": {
                "@type": "issue-credential/2.0/credential-preview",
                "attributes": props['attributes']
            },
            "filter": {
                "indy": {
                    "cred_def_id": props["cred_def_id"],
                    "issuer_did": props["issuer_did"],
                    "schema_id": props["schema_id"],
                    "schema_name": props["schema_id"].split(":")[2],
                    "schema_version": props["schema_id"].split(":")[3]
                }
            }
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                return self._fields(response.json(), ["cred_ex_id", "connection_id", "created_at", "updated_at", "state"])
            else:
                logging.error(f"Falha ao enviar oferta de credencial. Corpo da resposta: {response.text}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def send_request(self, cred_ex_id: str, auto_remove: bool = True):
        endpoint = f"{self.url}/issue-credential-2.0/records/{cred_ex_id}/send-request"
        body = {
            "auto_remove": auto_remove
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Pedido de credencial enviado com sucesso.")
                return self._fields(response.json(), ["cred_ex_id", "connection_id", "created_at", "updated_at", "state"])
            else:
                logging.error(f"Falha ao enviar pedido de credencial. Corpo da resposta: {response.text}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def issue_credential(self, cred_ex_id: str):
        endpoint = f"{self.url}/issue-credential-2.0/records/{cred_ex_id}/issue"
        body = {}

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Credencial emitida com sucesso.")
                return self._fields(response.json(), ["cred_ex_id", "connection_id", "created_at", "updated_at", "state"])
            else:
                logging.error(f"Falha ao emitir credencial. Corpo da resposta: {response.text}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None

    def store_credential(self, cred_ex_id: str):
        endpoint = f"{self.url}/issue-credential-2.0/records/{cred_ex_id}/store"
        body = {}

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Credencial armazenada com sucesso.")
                return self._fields(response.json(), ["cred_ex_id", "connection_id", "created_at", "updated_at", "state"])
            else:
                logging.error(f"Falha ao armazenar credencial. Corpo da resposta: {response.text}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_offers(self, cred_ex_id: str = None):
        endpoint = f"{self.url}/issue-credential-2.0/records"
        if cred_ex_id:
            endpoint += f"/{cred_ex_id}"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, timeout=10.0)

            if response.status_code == 200:
                logging.info(f"Ofertas de credenciais obtidas com sucesso.")
                return self._fields(response.json(), [
                    "cred_ex_id", 
                    "connection_id", 
                    "created_at", 
                    "updated_at", 
                    "state", 
                    "cred_preview",
                    "filter",
                    "schema_id",
                    "cred_def_id",
                    "schema_name",
                    "schema_version"
                ])
            else:
                logging.error(f"Falha ao obter ofertas de credenciais. Corpo da resposta: {response.text}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_stored_credentials(self):
        endpoint = f"{self.url}/credentials"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, timeout=10.0)
            response.raise_for_status()

            if response.status_code == 200:
                logging.info(f"Credenciais armazenadas obtidas com sucesso.")
                return self._fields(response.json(), [
                    "referent", 
                    "schema_id", 
                    "cred_def_id", 
                    "attrs", 
                    "created_at"
                ])
            else:
                logging.error(f"Falha ao obter credenciais armazenadas. Corpo da resposta: {response.text}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
class ClientVerify(Base):
    def __init__(self, url: str):
        self.url = url
        logging.info(f"ClientVerify inicializado com URL base: {self.url}")

    def send_proof_request(self, props: dict):
        if "auto_issue" not in props:
            props["auto_issue"] = True
        if "auto_remove" not in props:
            props["auto_remove"] = True

        if "connection_id" not in props:
            logging.error("Parâmetro obrigatório ausente: 'connection_id'")
            return None
        if "version" not in props:
            logging.error("Parâmetro obrigatório ausente: 'version'")
            return None
        if "schema_name" not in props:
            logging.error("Parâmetro obrigatório ausente: 'schema_name'")
            return None
        if "requested_attributes" not in props:
            logging.error("Parâmetro obrigatório ausente: 'requested_attributes'")
            return None
        
        endpoint = f"{self.url}/present-proof-2.0/send-request"
        body = {
            "auto_issue": props["auto_issue"],
            "auto_remove": props["auto_remove"],
            "connection_id": props["connection_id"],
            "presentation_request": {
                "indy": {
                    "name": f"Prova de credencial: {props['schema_name']}",
                    "version": props["version"],
                    "requested_attributes": props["requested_attributes"],
                    "requested_predicates": props.get("requested_predicates", {})
                }
            }
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)
            response.raise_for_status()
            logging.info(f"Pedido de prova enviado com sucesso.")
            return self._fields(response.json(), ["pres_ex_id", "connection_id", "created_at", "updated_at", "state"])
        except httpx.HTTPStatusError as e:
            logging.error(f"Falha ao enviar pedido de prova. Corpo da resposta: {e.response.text}")
            return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None

    def send_presentation(self, props: dict):
        if "auto_remove" not in props:
            props["auto_remove"] = True

        if "pres_ex_id" not in props:
            logging.error("Parâmetro obrigatório ausente: 'pres_ex_id'")
            return None
        if "requested_attributes" not in props:
            logging.error("Parâmetro obrigatório ausente: 'requested_attributes'")
            return None

        endpoint = f"{self.url}/present-proof-2.0/records/{props['pres_ex_id']}/send-presentation"
        body = {
            "indy": {
                "requested_attributes": props["requested_attributes"],
                "requested_predicates": props.get("requested_predicates", {}),
                "self_attested_attributes": props.get("self_attested_attributes", {})
            },
            "auto_remove": props["auto_remove"]
        }

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.post(endpoint, json=body, timeout=10.0)
            response.raise_for_status()
            logging.info(f"Prova enviada com sucesso.")
            return self._fields(response.json(), ["pres_ex_id", "connection_id", "created_at", "updated_at", "state"])
        except httpx.HTTPStatusError as e:
            logging.error(f"Falha ao enviar prova. Corpo da resposta: {e.response.text}")
            return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None
        
    def get_proof(self, pres_ex_id: str):
        endpoint = f"{self.url}/present-proof-2.0/records/{pres_ex_id}"

        logging.info(f"Enviando requisição para {endpoint}")

        try:
            response = httpx.get(endpoint, timeout=10.0)
            response.raise_for_status()
            logging.info(f"Prova obtida com sucesso.")
            return self._fields(response.json(), ["pres_ex_id", "connection_id", "created_at", "updated_at", "state", "verified"])
        except httpx.HTTPStatusError as e:
            logging.error(f"Falha ao obter prova. Corpo da resposta: {e.response.text}")
            return None
        except httpx.RequestError as e:
            logging.error(f"Erro de conexão com o ACA-Py: {e}")
            return None
        except Exception as e:
            logging.exception(f"Erro inesperado: {e}")
            return None