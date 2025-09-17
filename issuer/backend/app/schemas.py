"""
Pydantic models for request/response validation
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Request models
class UserRegisterRequest(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (minimum 6 characters)")
    first_name: Optional[str] = Field(None, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")

class UserLoginRequest(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

# Response models
class UserResponse(BaseModel):
    """User response model"""
    id: str = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    is_active: bool = Field(..., description="Whether user account is active")
    did: Optional[str] = Field(None, description="User's Decentralized Identifier")
    verkey: Optional[str] = Field(None, description="User's verification key")
    created_at: str = Field(..., description="Account creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

class AuthResponse(BaseModel):
    """Authentication response model"""
    token: str = Field(..., description="JWT access token")
    user: UserResponse = Field(..., description="User information")

class SSIStatusResponse(BaseModel):
    """SSI service status response model"""
    ssi_service_available: bool = Field(..., description="Whether SSI service is available")
    acapy_url: Optional[str] = Field(None, description="ACA-Py admin URL")
    user_has_did: bool = Field(..., description="Whether user has a DID")
    user_did: Optional[str] = Field(None, description="User's DID")
    user_verkey: Optional[str] = Field(None, description="User's verification key")
    did_metadata: Optional[Dict[str, Any]] = Field(None, description="DID metadata")
    error: Optional[str] = Field(None, description="Error message if service unavailable")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class ErrorResponse(BaseModel):
    """Error response model"""
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    errors: Optional[Dict[str, Any]] = Field(None, description="Validation errors")

# Connection/Invitation models
class ConnectionInvitationRequest(BaseModel):
    """Connection invitation request model"""
    connection_alias: str = Field(..., description="Alias/name for the connection")
    invitation_url: str = Field(..., description="URL containing the invitation")

class InvitationResponse(BaseModel):
    """Invitation processing response model"""
    success: bool = Field(..., description="Whether invitation was processed successfully")
    connection_id: Optional[str] = Field(None, description="Connection ID created")
    invitation_data: Optional[Dict[str, Any]] = Field(None, description="Parsed invitation data")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")

class ReceiveInvitationPayload(BaseModel):
    """Payload ready for /receive-invitation endpoint"""
    invitation: Dict[str, Any] = Field(..., description="Invitation object")
    auto_accept: Optional[bool] = Field(True, description="Auto accept the connection")
    alias: Optional[str] = Field(None, description="Alias for the connection")

# Internal models
class DIDInfo(BaseModel):
    """DID information model"""
    did: str = Field(..., description="Decentralized Identifier")
    verkey: str = Field(..., description="Verification key")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="DID metadata")
    alias: Optional[str] = Field(None, description="DID alias")
    registered_on_ledger: bool = Field(default=False, description="Whether DID is registered on ledger")

# SSI Issuer specific schemas

# Connection models
class ConnectionRecord(BaseModel):
    """Connection record response model"""
    connection_id: str = Field(..., description="Connection ID")
    state: str = Field(..., description="Connection state")
    their_label: Optional[str] = Field(None, description="Their connection label")
    their_did: Optional[str] = Field(None, description="Their DID")
    their_public_did: Optional[str] = Field(None, description="Their public DID")
    my_did: Optional[str] = Field(None, description="Our DID for this connection")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    alias: Optional[str] = Field(None, description="Connection alias")

class CreateInvitationResponse(BaseModel):
    """Create invitation response model"""
    connection_id: str = Field(..., description="Connection ID created")
    invitation_url: str = Field(..., description="Invitation URL")
    alias: Optional[str] = Field(None, description="Connection alias")

# Schema models
class SchemaResponse(BaseModel):
    """Schema response model"""
    schema_id: str = Field(..., description="Schema ID on the ledger")
    schema_def: Dict[str, Any] = Field(..., description="Schema definition")
    schema_name: str = Field(..., description="Schema name")
    schema_version: str = Field(..., description="Schema version")
    attributes: list[str] = Field(..., description="Schema attributes")

class CreateSchemaRequest(BaseModel):
    """Create schema request model"""
    schema_name: str = Field(..., description="Name of the schema")
    schema_version: str = Field(..., description="Version of the schema")
    attributes: list[str] = Field(..., description="List of attribute names")

# Credential Definition models
class CredentialDefinitionResponse(BaseModel):
    """Credential definition response model"""
    credential_definition_id: str = Field(..., description="Credential definition ID")
    credential_definition: Dict[str, Any] = Field(..., description="Credential definition object")
    schema_id: str = Field(..., description="Associated schema ID")

class CreateCredentialDefinitionRequest(BaseModel):
    """Create credential definition request model"""
    schema_id: str = Field(..., description="Schema ID to base the credential definition on")
    tag: Optional[str] = Field("default", description="Tag for the credential definition")
    support_revocation: Optional[bool] = Field(False, description="Support credential revocation")

# Credential Exchange models
class CredentialExchangeRecord(BaseModel):
    """Credential exchange record model"""
    credential_exchange_id: str = Field(..., description="Credential exchange ID")
    connection_id: str = Field(..., description="Connection ID")
    state: str = Field(..., description="Exchange state")
    credential_definition_id: Optional[str] = Field(None, description="Credential definition ID")
    schema_id: Optional[str] = Field(None, description="Schema ID")
    credential_proposal: Optional[Dict[str, Any]] = Field(None, description="Credential proposal")
    credential_offer: Optional[Dict[str, Any]] = Field(None, description="Credential offer")
    credential: Optional[Dict[str, Any]] = Field(None, description="Issued credential")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

class SendCredentialOfferRequest(BaseModel):
    """Send credential offer request model"""
    connection_id: str = Field(..., description="Connection ID to send offer to")
    credential_definition_id: str = Field(..., description="Credential definition ID")
    credential_preview: Dict[str, Any] = Field(..., description="Credential attributes preview")
    comment: Optional[str] = Field(None, description="Comment for the credential offer")

class IssueCredentialRequest(BaseModel):
    """Issue credential request model"""
    credential_exchange_id: str = Field(..., description="Credential exchange ID")
    comment: Optional[str] = Field(None, description="Comment for issuing credential")

# User connection tracking models
class UserConnectionResponse(BaseModel):
    """User connection response model"""
    user_id: str = Field(..., description="Internal user ID")
    connection_id: str = Field(..., description="ACA-Py connection ID")
    their_label: Optional[str] = Field(None, description="Their connection label")
    their_did: Optional[str] = Field(None, description="Their DID")
    state: str = Field(..., description="Connection state")
    created_at: str = Field(..., description="Connection creation timestamp")

class ShowUsersResponse(BaseModel):
    """Show connected users response model"""
    total_users: int = Field(..., description="Total number of connected users")
    users: list[UserConnectionResponse] = Field(..., description="List of connected users")

# Offer tracking models
class OfferResponse(BaseModel):
    """Credential offer response model"""
    offer_id: str = Field(..., description="Internal offer ID")
    credential_exchange_id: str = Field(..., description="ACA-Py credential exchange ID")
    connection_id: str = Field(..., description="Connection ID")
    user_id: Optional[str] = Field(None, description="Internal user ID")
    their_label: Optional[str] = Field(None, description="Recipient label")
    credential_definition_id: str = Field(..., description="Credential definition ID")
    schema_name: str = Field(..., description="Schema name")
    state: str = Field(..., description="Offer state")
    attributes: Dict[str, Any] = Field(..., description="Credential attributes")
    created_at: str = Field(..., description="Offer creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

class ShowOffersResponse(BaseModel):
    """Show offers response model"""
    total_offers: int = Field(..., description="Total number of offers")
    pending_offers: int = Field(..., description="Number of pending offers")
    completed_offers: int = Field(..., description="Number of completed offers")
    offers: list[OfferResponse] = Field(..., description="List of offers")

# Certificate tracking models
class CertificateResponse(BaseModel):
    """Certificate response model"""
    certificate_id: str = Field(..., description="Internal certificate ID")
    credential_exchange_id: str = Field(..., description="ACA-Py credential exchange ID")
    connection_id: str = Field(..., description="Connection ID")
    user_id: Optional[str] = Field(None, description="Internal user ID")
    recipient_label: Optional[str] = Field(None, description="Recipient label")
    schema_name: str = Field(..., description="Schema name")
    credential_definition_id: str = Field(..., description="Credential definition ID")
    attributes: Dict[str, Any] = Field(..., description="Certificate attributes")
    state: str = Field(..., description="Certificate state")
    issued_at: str = Field(..., description="Issuance timestamp")

# Generic responses
class SuccessResponse(BaseModel):
    """Generic success response model"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")