"""
Pydantic models for request/response validation
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime
import json
import base64
import urllib.parse

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