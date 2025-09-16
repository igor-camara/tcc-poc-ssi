import asyncio
import json
import base64
import urllib.parse
from typing import Dict, Any, List, Optional
from aries_cloudcontroller import AcaPyClient
from app.config import settings
from app.models.ssi_models import (
    ConnectionModel, SchemaModel, CredentialOfferModel, 
    IssuedCertificateModel, DatabaseManager
)

class SSIService:
    """Service for SSI operations with ACA-Py"""
    
    def __init__(self):
        self.controller = None
        self._initialize_controller()
    
    def _initialize_controller(self):
        """Initialize ACA-Py controller"""
        try:
            admin_url = settings.acapy_admin_url
            api_key = settings.acapy_admin_api_key
            
            if not admin_url:
                raise ValueError("ACAPY_ADMIN_URL not configured")
            
            self.controller = AcaPyClient(
                admin_url, 
                api_key=api_key if api_key else None
            )
            
            print(f"SSI Service initialized with ACA-Py at {admin_url}")
            
        except Exception as e:
            print(f"Failed to initialize SSI Service: {str(e)}")
            raise
    
    # ============ Connection Management ============
    
    async def create_invitation(self, alias: Optional[str] = None, auto_accept: bool = True) -> Dict[str, Any]:
        """
        Create a connection invitation
        
        Args:
            alias: Optional alias for the connection
            auto_accept: Whether to auto accept the connection
            
        Returns:
            dict: Invitation data including connection_id, invitation, and invitation_url
        """
        try:
            # Create invitation using ACA-Py
            result = await self.controller.connection.create_invitation(
                alias=alias,
                auto_accept=auto_accept,
                public=True,  # Use public DID if available
                multi_use=False  # Single use invitation
            )
            
            invitation_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            # Store connection in database
            connection = ConnectionModel(
                connection_id=invitation_data["connection_id"],
                state="invitation",
                alias=alias,
                metadata={"auto_accept": auto_accept}
            )
            connection.save()
            
            print(f"Created invitation for connection {invitation_data['connection_id']}")
            return invitation_data
            
        except Exception as e:
            print(f"Failed to create invitation: {str(e)}")
            raise Exception(f"Erro ao criar convite: {str(e)}")
    
    async def get_connections(self) -> List[Dict[str, Any]]:
        """
        Get all connections from ACA-Py and sync with database
        
        Returns:
            list: List of connection records
        """
        try:
            # Get connections from ACA-Py
            result = await self.controller.connection.get_connections()
            connections_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            connections = []
            for conn_data in connections_data.get("results", []):
                # Update database with latest info
                connection = ConnectionModel.get_by_connection_id(conn_data["connection_id"])
                if connection:
                    connection.state = conn_data.get("state", connection.state)
                    connection.their_label = conn_data.get("their_label", connection.their_label)
                    connection.their_did = conn_data.get("their_did", connection.their_did)
                    connection.their_public_did = conn_data.get("their_public_did", connection.their_public_did)
                    connection.my_did = conn_data.get("my_did", connection.my_did)
                    connection.save()
                else:
                    # Create new connection record
                    connection = ConnectionModel(
                        connection_id=conn_data["connection_id"],
                        state=conn_data.get("state", "unknown"),
                        their_label=conn_data.get("their_label"),
                        their_did=conn_data.get("their_did"),
                        their_public_did=conn_data.get("their_public_did"),
                        my_did=conn_data.get("my_did"),
                        alias=conn_data.get("alias")
                    )
                    connection.save()
                
                connections.append(conn_data)
            
            return connections
            
        except Exception as e:
            print(f"Failed to get connections: {str(e)}")
            raise Exception(f"Erro ao buscar conexões: {str(e)}")
    
    async def get_active_connections(self) -> List[ConnectionModel]:
        """
        Get all active connections
        
        Returns:
            list: List of active ConnectionModel instances
        """
        try:
            # Sync with ACA-Py first
            await self.get_connections()
            
            # Return active connections from database
            return ConnectionModel.get_all_active_connections()
            
        except Exception as e:
            print(f"Failed to get active connections: {str(e)}")
            raise Exception(f"Erro ao buscar conexões ativas: {str(e)}")
    
    # ============ Schema Management ============
    
    async def create_schema(self, schema_name: str, schema_version: str, attributes: List[str], created_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new credential schema on the ledger
        
        Args:
            schema_name: Name of the schema
            schema_version: Version of the schema
            attributes: List of attribute names
            created_by: User ID who created the schema
            
        Returns:
            dict: Schema creation result
        """
        try:
            # Create schema using ACA-Py
            schema_body = {
                "schema_name": schema_name,
                "schema_version": schema_version,
                "attributes": attributes
            }
            
            result = await self.controller.schema.publish_schema(body=schema_body)
            schema_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            # Store schema in database
            schema = SchemaModel(
                schema_id=schema_data["schema_id"],
                schema_name=schema_name,
                schema_version=schema_version,
                attributes=attributes,
                schema_definition=schema_data,
                created_by=created_by
            )
            schema.save()
            
            print(f"Created schema {schema_data['schema_id']}")
            return schema_data
            
        except Exception as e:
            print(f"Failed to create schema: {str(e)}")
            raise Exception(f"Erro ao criar schema: {str(e)}")
    
    async def create_credential_definition(self, schema_id: str, tag: str = "default", support_revocation: bool = False) -> Dict[str, Any]:
        """
        Create a credential definition based on a schema
        
        Args:
            schema_id: Schema ID to base the credential definition on
            tag: Tag for the credential definition
            support_revocation: Whether to support revocation
            
        Returns:
            dict: Credential definition creation result
        """
        try:
            # Create credential definition using ACA-Py
            cred_def_body = {
                "schema_id": schema_id,
                "tag": tag,
                "support_revocation": support_revocation
            }
            
            result = await self.controller.credential_definition.publish_cred_def(body=cred_def_body)
            cred_def_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            print(f"Created credential definition {cred_def_data['credential_definition_id']}")
            return cred_def_data
            
        except Exception as e:
            print(f"Failed to create credential definition: {str(e)}")
            raise Exception(f"Erro ao criar definição de credencial: {str(e)}")
    
    # ============ Credential Offer Management ============
    
    async def send_credential_offer(self, connection_id: str, credential_definition_id: str, 
                                  credential_preview: Dict[str, Any], comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a credential offer to a connection
        
        Args:
            connection_id: Connection ID to send offer to
            credential_definition_id: Credential definition ID
            credential_preview: Credential attributes preview
            comment: Optional comment
            
        Returns:
            dict: Credential exchange record
        """
        try:
            # Prepare credential offer
            offer_body = {
                "connection_id": connection_id,
                "credential_definition_id": credential_definition_id,
                "credential_preview": credential_preview,
                "auto_issue": False,  # Manual issuing for better control
                "auto_remove": False,
                "comment": comment
            }
            
            # Send offer using ACA-Py
            result = await self.controller.issue_credential_v1_0.send_offer(body=offer_body)
            exchange_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            # Get schema info for display
            schema = SchemaModel.get_by_schema_id(
                credential_definition_id.split(":")[0] + ":" + 
                credential_definition_id.split(":")[1] + ":" + 
                credential_definition_id.split(":")[3] + ":" + 
                credential_definition_id.split(":")[4]
            )
            schema_name = schema.schema_name if schema else "Unknown Schema"
            
            # Store offer in database
            offer = CredentialOfferModel(
                credential_exchange_id=exchange_data["credential_exchange_id"],
                connection_id=connection_id,
                credential_definition_id=credential_definition_id,
                schema_name=schema_name,
                attributes=credential_preview.get("attributes", {}),
                state=exchange_data.get("state", "offer_sent"),
                comment=comment
            )
            offer.save()
            
            print(f"Sent credential offer {exchange_data['credential_exchange_id']}")
            return exchange_data
            
        except Exception as e:
            print(f"Failed to send credential offer: {str(e)}")
            raise Exception(f"Erro ao enviar oferta de credencial: {str(e)}")
    
    async def get_credential_exchanges(self) -> List[Dict[str, Any]]:
        """
        Get all credential exchange records from ACA-Py
        
        Returns:
            list: List of credential exchange records
        """
        try:
            result = await self.controller.issue_credential_v1_0.get_records()
            exchanges_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            return exchanges_data.get("results", [])
            
        except Exception as e:
            print(f"Failed to get credential exchanges: {str(e)}")
            raise Exception(f"Erro ao buscar trocas de credenciais: {str(e)}")
    
    async def get_offers(self) -> List[CredentialOfferModel]:
        """
        Get all credential offers with latest status
        
        Returns:
            list: List of CredentialOfferModel instances
        """
        try:
            # Sync with ACA-Py
            exchanges = await self.get_credential_exchanges()
            
            # Update database with latest states
            for exchange in exchanges:
                offer = CredentialOfferModel.get_by_exchange_id(exchange["credential_exchange_id"])
                if offer:
                    offer.state = exchange.get("state", offer.state)
                    offer.save()
            
            return CredentialOfferModel.get_all_offers()
            
        except Exception as e:
            print(f"Failed to get offers: {str(e)}")
            raise Exception(f"Erro ao buscar ofertas: {str(e)}")
    
    # ============ Credential Issuance ============
    
    async def issue_credential(self, credential_exchange_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Issue a credential for an accepted offer
        
        Args:
            credential_exchange_id: Credential exchange ID
            comment: Optional comment
            
        Returns:
            dict: Issued credential data
        """
        try:
            # Get the credential exchange record
            result = await self.controller.issue_credential_v1_0.get_record(credential_exchange_id)
            exchange_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            if exchange_data.get("state") != "request_received":
                raise ValueError(f"Cannot issue credential in state: {exchange_data.get('state')}")
            
            # Issue the credential
            issue_body = {
                "comment": comment
            }
            
            result = await self.controller.issue_credential_v1_0.issue_credential(
                credential_exchange_id, body=issue_body
            )
            issued_data = result.to_dict() if hasattr(result, 'to_dict') else result
            
            # Get offer info for certificate record
            offer = CredentialOfferModel.get_by_exchange_id(credential_exchange_id)
            
            # Store issued certificate in database
            certificate = IssuedCertificateModel(
                credential_exchange_id=credential_exchange_id,
                connection_id=exchange_data["connection_id"],
                credential_definition_id=exchange_data["credential_definition_id"],
                schema_name=offer.schema_name if offer else "Unknown Schema",
                attributes=offer.attributes if offer else {},
                state=issued_data.get("state", "credential_issued"),
                credential_data=issued_data.get("credential", {})
            )
            certificate.save()
            
            print(f"Issued credential {credential_exchange_id}")
            return issued_data
            
        except Exception as e:
            print(f"Failed to issue credential: {str(e)}")
            raise Exception(f"Erro ao emitir credencial: {str(e)}")
    
    # ============ Utility Methods ============
    
    async def create_did(self, alias=None):
        """
        Create a new DID for the user
        
        Args:
            alias: Optional alias for the DID
            
        Returns:
            dict: DID information including did, verkey, etc.
        """
        try:
            # Create a new local DID
            result = await self.controller.wallet.create_did(body={"key_type": "ed25519"})
            
            did_info = result.result.to_dict()
            
            print(f"Created DID: {did_info.get('did')} with verkey: {did_info.get('verkey')}")
            
            return {
                'did': did_info.get('did'),
                'verkey': did_info.get('verkey'),
                'metadata': did_info.get('metadata', {}),
                'alias': alias
            }
            
        except Exception as e:
            print(f"Failed to create DID: {str(e)}")
            raise Exception(f"Erro ao criar DID: {str(e)}")
    
    async def register_did_on_ledger(self, did, verkey, alias=None):
        """
        Register DID on the ledger (von-network)
        
        Args:
            did: DID to register
            verkey: Verification key
            alias: Optional alias
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.controller.ledger.register_nym(
                did=did,
                verkey=verkey,
                alias=alias,
                role=None  # Regular identity, not a trustee/steward
            )
            
            print(f"Registered DID {did} on ledger")
            return True
            
        except Exception as e:
            print(f"Failed to register DID on ledger: {str(e)}")
            print("Continuing without ledger registration")
            return False
            
            print(f"Created DID: {did_info.get('did')} with verkey: {did_info.get('verkey')}")
            
            return {
                'did': did_info.get('did'),
                'verkey': did_info.get('verkey'),
                'metadata': did_info.get('metadata', {}),
                'alias': alias
            }
            
        except Exception as e:
            print(f"Failed to create DID: {str(e)}")
            raise Exception(f"Erro ao criar DID: {str(e)}")
    
    async def register_did_on_ledger(self, did, verkey, alias=None):
        """
        Register DID on the ledger (von-network)
        
        Args:
            did: DID to register
            verkey: Verification key
            alias: Optional alias
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.controller.ledger.register_nym(
                did=did,
                verkey=verkey,
                alias=alias,
                role=None  # Regular identity, not a trustee/steward
            )
            
            print(f"Registered DID {did} on ledger")
            return True
            
        except Exception as e:
            print(f"Failed to register DID on ledger: {str(e)}")
            print("Continuing without ledger registration")
            return False
    
    async def create_and_register_did(self, user_email):
        """
        Create a new DID and optionally register it on the ledger
        
        Args:
            user_email: User email to use as alias
            
        Returns:
            dict: Complete DID information
        """
        try:
            # Create DID
            did_info = await self.create_did(alias=user_email)
            
            # Try to register on ledger (optional for MVP)
            try:
                await self.register_did_on_ledger(
                    did_info['did'], 
                    did_info['verkey'], 
                    user_email
                )
                did_info['registered_on_ledger'] = True
            except:
                did_info['registered_on_ledger'] = False
                print("DID not registered on ledger, but created locally")
            
            return did_info
            
        except Exception as e:
            print(f"Failed to create and register DID: {str(e)}")
            raise

    async def parse_invitation_url(self, invitation_url):
        """
        Parse invitation URL to extract invitation data
        
        Args:
            invitation_url: URL containing the invitation (could be c_i or oob parameter)
            
        Returns:
            dict: Parsed invitation data
        """
        try:
            print(f"Parsing invitation URL: {invitation_url}")
            
            # Parse the URL
            parsed_url = urllib.parse.urlparse(invitation_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            print(f"Parsed URL components: scheme={parsed_url.scheme}, netloc={parsed_url.netloc}, path={parsed_url.path}")
            print(f"Query parameters found: {list(query_params.keys())}")
            
            invitation_data = None
            
            # Try to find invitation in different parameter formats
            if 'c_i' in query_params:
                print("Found 'c_i' parameter - processing as connection invitation")
                invitation_b64 = query_params['c_i'][0]
                print(f"Base64 invitation data (first 50 chars): {invitation_b64[:50]}...")
                
                try:
                    # Add padding if needed
                    padding = len(invitation_b64) % 4
                    if padding:
                        invitation_b64 += '=' * (4 - padding)
                    
                    invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                    invitation_data = json.loads(invitation_json)
                    print("Successfully decoded c_i parameter")
                except Exception as decode_error:
                    print(f"Failed to decode c_i parameter: {decode_error}")
                    raise
                
            elif 'oob' in query_params:
                print("Found 'oob' parameter - processing as out-of-band invitation")
                invitation_b64 = query_params['oob'][0]
                print(f"Base64 invitation data (first 50 chars): {invitation_b64[:50]}...")
                
                try:
                    # Add padding if needed
                    padding = len(invitation_b64) % 4
                    if padding:
                        invitation_b64 += '=' * (4 - padding)
                    
                    invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                    invitation_data = json.loads(invitation_json)
                    print("Successfully decoded oob parameter")
                except Exception as decode_error:
                    print(f"Failed to decode oob parameter: {decode_error}")
                    raise
                
            elif 'd_m' in query_params:
                print("Found 'd_m' parameter - processing as DIDComm message")
                invitation_b64 = query_params['d_m'][0]
                print(f"Base64 invitation data (first 50 chars): {invitation_b64[:50]}...")
                
                try:
                    # Add padding if needed
                    padding = len(invitation_b64) % 4
                    if padding:
                        invitation_b64 += '=' * (4 - padding)
                    
                    invitation_json = base64.urlsafe_b64decode(invitation_b64).decode('utf-8')
                    invitation_data = json.loads(invitation_json)
                    print("Successfully decoded d_m parameter")
                except Exception as decode_error:
                    print(f"Failed to decode d_m parameter: {decode_error}")
                    raise
                
            else:
                # Check if the URL might be a different format
                if parsed_url.query:
                    print(f"No standard invitation parameters found. Raw query: {parsed_url.query}")
                    
                    # Try to decode the entire query as base64
                    try:
                        padding = len(parsed_url.query) % 4
                        query_with_padding = parsed_url.query + ('=' * (4 - padding) if padding else '')
                        invitation_json = base64.urlsafe_b64decode(query_with_padding).decode('utf-8')
                        invitation_data = json.loads(invitation_json)
                        print("Successfully decoded entire query as base64")
                    except Exception as decode_error:
                        print(f"Failed to decode query as base64: {decode_error}")
                        
                        # Check if it's already JSON
                        try:
                            invitation_data = json.loads(urllib.parse.unquote(parsed_url.query))
                            print("Successfully parsed query as JSON")
                        except Exception as json_error:
                            print(f"Failed to parse query as JSON: {json_error}")
                            raise ValueError(f"Unable to parse invitation from URL. Query: {parsed_url.query}")
                else:
                    # Check if the entire URL might be base64 encoded
                    if '?' not in invitation_url and '=' in invitation_url:
                        print("No query parameters found, trying to decode entire URL as base64")
                        try:
                            # Remove any URL prefix and try to decode
                            potential_b64 = invitation_url.split('/')[-1] if '/' in invitation_url else invitation_url
                            padding = len(potential_b64) % 4
                            if padding:
                                potential_b64 += '=' * (4 - padding)
                            
                            invitation_json = base64.urlsafe_b64decode(potential_b64).decode('utf-8')
                            invitation_data = json.loads(invitation_json)
                            print("Successfully decoded URL as base64")
                        except Exception as decode_error:
                            print(f"Failed to decode URL as base64: {decode_error}")
                            raise ValueError("No invitation data found in URL and unable to decode as base64")
                    else:
                        raise ValueError("No invitation data found in URL")
            
            if not invitation_data:
                raise ValueError("No valid invitation data found in URL")
                
            print(f"Successfully parsed invitation: {json.dumps(invitation_data, indent=2)}")
            return invitation_data
            
        except Exception as e:
            print(f"Failed to parse invitation URL: {str(e)}")
            raise Exception(f"Erro ao processar URL do convite: {str(e)}")

    async def prepare_receive_invitation_payload(self, connection_alias, invitation_url):
        """
        Prepare payload for receive-invitation endpoint
        
        Args:
            connection_alias: Alias for the connection
            invitation_url: URL containing the invitation
            
        Returns:
            dict: Payload ready for receive-invitation
        """
        try:
            # Parse the invitation from URL
            invitation_data = await self.parse_invitation_url(invitation_url)
            
            # Prepare the payload
            payload = {
                "invitation": invitation_data,
                "auto_accept": True,
                "alias": connection_alias
            }
            
            print(f"Prepared receive-invitation payload: {payload}")
            return payload
            
        except Exception as e:
            print(f"Failed to prepare receive-invitation payload: {str(e)}")
            raise

    async def receive_invitation(self, invitation_payload):
        """
        Receive and process a connection invitation
        
        Args:
            invitation_payload: Payload containing invitation data
            
        Returns:
            dict: Connection result
        """
        try:
            # Use ACA-Py's connection API to receive the invitation
            result = await self.controller.connection.receive_invitation(
                body=invitation_payload["invitation"],
                alias=invitation_payload.get("alias"),
                auto_accept=invitation_payload.get("auto_accept", True)
            )
            
            connection_info = result.to_dict() if hasattr(result, 'to_dict') else result
            
            print(f"Received invitation successfully: {connection_info}")
            return connection_info
            
        except Exception as e:
            print(f"Failed to receive invitation: {str(e)}")
            raise Exception(f"Erro ao aceitar convite: {str(e)}")

# Singleton instance
ssi_service = None

def get_ssi_service():
    """Get or create SSI service instance"""
    global ssi_service
    if ssi_service is None:
        ssi_service = SSIService()
    return ssi_service