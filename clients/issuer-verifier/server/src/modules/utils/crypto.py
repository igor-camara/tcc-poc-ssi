"""
Utility functions for cryptographic operations in SSI context
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
import base64
import json


class DIDCrypto:
    """Handle DID cryptographic operations"""
    
    @staticmethod
    def generate_keypair() -> Tuple[str, str]:
        """
        Generate Ed25519 keypair for DID
        Returns: (private_key_pem, public_key_pem)
        """
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    @staticmethod
    def generate_did(public_key_pem: str) -> str:
        """
        Generate DID from public key
        Using did:key method for simplicity
        """
        # Extract raw public key bytes
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Create multibase encoded key (Ed25519 prefix: 0xed01)
        multicodec_key = b'\xed\x01' + public_bytes
        multibase_key = base64.urlsafe_b64encode(multicodec_key).decode('utf-8').rstrip('=')
        
        return f"did:key:z{multibase_key}"
    
    @staticmethod
    def sign_challenge(private_key_pem: str, challenge: str) -> str:
        """
        Sign a challenge with private key
        Returns base64 encoded signature
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(challenge.encode('utf-8'))
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify_signature(public_key_pem: str, challenge: str, signature_b64: str) -> bool:
        """
        Verify signature against challenge
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            signature = base64.b64decode(signature_b64)
            public_key.verify(signature, challenge.encode('utf-8'))
            return True
        except Exception:
            return False


class ChallengeManager:
    """Manage authentication challenges"""
    
    # In-memory storage for challenges (in production, use Redis or database)
    _challenges: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def generate_challenge(cls, did: str, expiry_minutes: int = 5) -> str:
        """
        Generate a random challenge for authentication
        """
        challenge = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        cls._challenges[challenge] = {
            'did': did,
            'expires_at': expires_at,
            'used': False
        }
        
        return challenge
    
    @classmethod
    def validate_challenge(cls, challenge: str, did: str) -> bool:
        """
        Validate that challenge exists, hasn't expired, and belongs to the DID
        """
        if challenge not in cls._challenges:
            return False
        
        challenge_data = cls._challenges[challenge]
        
        # Check if expired
        if datetime.utcnow() > challenge_data['expires_at']:
            cls._challenges.pop(challenge, None)
            return False
        
        # Check if already used
        if challenge_data['used']:
            return False
        
        # Check if DID matches
        if challenge_data['did'] != did:
            return False
        
        return True
    
    @classmethod
    def consume_challenge(cls, challenge: str) -> bool:
        """
        Mark challenge as used
        """
        if challenge in cls._challenges:
            cls._challenges[challenge]['used'] = True
            return True
        return False
    
    @classmethod
    def cleanup_expired(cls):
        """
        Remove expired challenges from memory
        """
        now = datetime.utcnow()
        expired_challenges = [
            challenge for challenge, data in cls._challenges.items()
            if now > data['expires_at']
        ]
        
        for challenge in expired_challenges:
            cls._challenges.pop(challenge, None)


def generate_secure_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure random string"""
    return secrets.token_urlsafe(length)


def hash_private_key(private_key: str, salt: str) -> str:
    """Hash private key for secure storage"""
    return hashlib.pbkdf2_hmac(
        'sha256',
        private_key.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    ).hex()