"""
SSI Models for storing metadata in SQLite
"""
import uuid
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

class DatabaseManager:
    """Database manager for SSI models"""
    
    @staticmethod
    def _get_db_connection():
        """Get database connection"""
        db_path = os.environ.get('DATABASE_URL', 'sqlite:///issuer.db').replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def init_ssi_tables():
        """Initialize SSI-related database tables"""
        conn = DatabaseManager._get_db_connection()
        
        # Connections table - tracks connections with users
        conn.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id TEXT PRIMARY KEY,
                connection_id TEXT UNIQUE NOT NULL,
                user_id TEXT,
                their_label TEXT,
                their_did TEXT,
                their_public_did TEXT,
                my_did TEXT,
                state TEXT NOT NULL,
                alias TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Schemas table - tracks credential schemas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schemas (
                id TEXT PRIMARY KEY,
                schema_id TEXT UNIQUE NOT NULL,
                schema_name TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                attributes TEXT NOT NULL,
                schema_definition TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Credential definitions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS credential_definitions (
                id TEXT PRIMARY KEY,
                credential_definition_id TEXT UNIQUE NOT NULL,
                schema_id TEXT NOT NULL,
                tag TEXT,
                support_revocation INTEGER DEFAULT 0,
                credential_definition TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT,
                FOREIGN KEY (schema_id) REFERENCES schemas (schema_id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Credential offers table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS credential_offers (
                id TEXT PRIMARY KEY,
                credential_exchange_id TEXT UNIQUE NOT NULL,
                connection_id TEXT NOT NULL,
                user_id TEXT,
                credential_definition_id TEXT NOT NULL,
                schema_name TEXT NOT NULL,
                state TEXT NOT NULL,
                attributes TEXT NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (connection_id) REFERENCES connections (connection_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (credential_definition_id) REFERENCES credential_definitions (credential_definition_id)
            )
        ''')
        
        # Issued certificates table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS issued_certificates (
                id TEXT PRIMARY KEY,
                credential_exchange_id TEXT UNIQUE NOT NULL,
                connection_id TEXT NOT NULL,
                user_id TEXT,
                credential_definition_id TEXT NOT NULL,
                schema_name TEXT NOT NULL,
                attributes TEXT NOT NULL,
                state TEXT NOT NULL,
                credential_data TEXT,
                issued_at TEXT NOT NULL,
                revoked_at TEXT,
                FOREIGN KEY (connection_id) REFERENCES connections (connection_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (credential_definition_id) REFERENCES credential_definitions (credential_definition_id)
            )
        ''')
        
        conn.commit()
        conn.close()

class ConnectionModel:
    """Model for managing connections"""
    
    def __init__(self, connection_id: str, user_id: Optional[str] = None,
                 their_label: Optional[str] = None, their_did: Optional[str] = None,
                 their_public_did: Optional[str] = None, my_did: Optional[str] = None,
                 state: str = "invitation", alias: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 id: Optional[str] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.connection_id = connection_id
        self.user_id = user_id
        self.their_label = their_label
        self.their_did = their_did
        self.their_public_did = their_public_did
        self.my_did = my_did
        self.state = state
        self.alias = alias
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def save(self):
        """Save connection to database"""
        conn = DatabaseManager._get_db_connection()
        
        conn.execute('''
            INSERT OR REPLACE INTO connections 
            (id, connection_id, user_id, their_label, their_did, their_public_did,
             my_did, state, alias, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.id, self.connection_id, self.user_id, self.their_label,
            self.their_did, self.their_public_did, self.my_did, self.state,
            self.alias, json.dumps(self.metadata), 
            self.created_at.isoformat(), self.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def get_by_connection_id(cls, connection_id: str):
        """Get connection by ACA-Py connection ID"""
        conn = DatabaseManager._get_db_connection()
        row = conn.execute(
            'SELECT * FROM connections WHERE connection_id = ?', 
            (connection_id,)
        ).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_active_connections(cls):
        """Get all active connections"""
        conn = DatabaseManager._get_db_connection()
        rows = conn.execute(
            'SELECT * FROM connections WHERE state IN ("active", "response") ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create ConnectionModel from database row"""
        return cls(
            id=row['id'],
            connection_id=row['connection_id'],
            user_id=row['user_id'],
            their_label=row['their_label'],
            their_did=row['their_did'],
            their_public_did=row['their_public_did'],
            my_did=row['my_did'],
            state=row['state'],
            alias=row['alias'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )

class SchemaModel:
    """Model for managing credential schemas"""
    
    def __init__(self, schema_id: str, schema_name: str, schema_version: str,
                 attributes: List[str], schema_definition: Dict[str, Any],
                 created_by: Optional[str] = None, id: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.schema_id = schema_id
        self.schema_name = schema_name
        self.schema_version = schema_version
        self.attributes = attributes
        self.schema_definition = schema_definition
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
    
    def save(self):
        """Save schema to database"""
        conn = DatabaseManager._get_db_connection()
        
        conn.execute('''
            INSERT OR REPLACE INTO schemas 
            (id, schema_id, schema_name, schema_version, attributes, 
             schema_definition, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.id, self.schema_id, self.schema_name, self.schema_version,
            json.dumps(self.attributes), json.dumps(self.schema_definition),
            self.created_at.isoformat(), self.created_by
        ))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def get_by_schema_id(cls, schema_id: str):
        """Get schema by schema ID"""
        conn = DatabaseManager._get_db_connection()
        row = conn.execute(
            'SELECT * FROM schemas WHERE schema_id = ?', 
            (schema_id,)
        ).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_schemas(cls):
        """Get all schemas"""
        conn = DatabaseManager._get_db_connection()
        rows = conn.execute(
            'SELECT * FROM schemas ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create SchemaModel from database row"""
        return cls(
            id=row['id'],
            schema_id=row['schema_id'],
            schema_name=row['schema_name'],
            schema_version=row['schema_version'],
            attributes=json.loads(row['attributes']),
            schema_definition=json.loads(row['schema_definition']),
            created_by=row['created_by'],
            created_at=datetime.fromisoformat(row['created_at'])
        )

class CredentialOfferModel:
    """Model for managing credential offers"""
    
    def __init__(self, credential_exchange_id: str, connection_id: str,
                 credential_definition_id: str, schema_name: str,
                 attributes: Dict[str, Any], state: str = "offer_sent",
                 user_id: Optional[str] = None, comment: Optional[str] = None,
                 id: Optional[str] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.credential_exchange_id = credential_exchange_id
        self.connection_id = connection_id
        self.user_id = user_id
        self.credential_definition_id = credential_definition_id
        self.schema_name = schema_name
        self.state = state
        self.attributes = attributes
        self.comment = comment
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def save(self):
        """Save offer to database"""
        conn = DatabaseManager._get_db_connection()
        
        conn.execute('''
            INSERT OR REPLACE INTO credential_offers 
            (id, credential_exchange_id, connection_id, user_id, 
             credential_definition_id, schema_name, state, attributes, 
             comment, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.id, self.credential_exchange_id, self.connection_id,
            self.user_id, self.credential_definition_id, self.schema_name,
            self.state, json.dumps(self.attributes), self.comment,
            self.created_at.isoformat(), self.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def get_by_exchange_id(cls, credential_exchange_id: str):
        """Get offer by credential exchange ID"""
        conn = DatabaseManager._get_db_connection()
        row = conn.execute(
            'SELECT * FROM credential_offers WHERE credential_exchange_id = ?', 
            (credential_exchange_id,)
        ).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_offers(cls):
        """Get all offers"""
        conn = DatabaseManager._get_db_connection()
        rows = conn.execute(
            'SELECT * FROM credential_offers ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_pending_offers(cls):
        """Get pending offers"""
        conn = DatabaseManager._get_db_connection()
        rows = conn.execute(
            'SELECT * FROM credential_offers WHERE state IN ("offer_sent", "request_received") ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create CredentialOfferModel from database row"""
        return cls(
            id=row['id'],
            credential_exchange_id=row['credential_exchange_id'],
            connection_id=row['connection_id'],
            user_id=row['user_id'],
            credential_definition_id=row['credential_definition_id'],
            schema_name=row['schema_name'],
            state=row['state'],
            attributes=json.loads(row['attributes']),
            comment=row['comment'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )

class IssuedCertificateModel:
    """Model for managing issued certificates"""
    
    def __init__(self, credential_exchange_id: str, connection_id: str,
                 credential_definition_id: str, schema_name: str,
                 attributes: Dict[str, Any], state: str = "credential_issued",
                 user_id: Optional[str] = None, credential_data: Optional[Dict[str, Any]] = None,
                 id: Optional[str] = None, issued_at: Optional[datetime] = None,
                 revoked_at: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.credential_exchange_id = credential_exchange_id
        self.connection_id = connection_id
        self.user_id = user_id
        self.credential_definition_id = credential_definition_id
        self.schema_name = schema_name
        self.attributes = attributes
        self.state = state
        self.credential_data = credential_data or {}
        self.issued_at = issued_at or datetime.utcnow()
        self.revoked_at = revoked_at
    
    def save(self):
        """Save certificate to database"""
        conn = DatabaseManager._get_db_connection()
        
        conn.execute('''
            INSERT OR REPLACE INTO issued_certificates 
            (id, credential_exchange_id, connection_id, user_id, 
             credential_definition_id, schema_name, attributes, state,
             credential_data, issued_at, revoked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.id, self.credential_exchange_id, self.connection_id,
            self.user_id, self.credential_definition_id, self.schema_name,
            json.dumps(self.attributes), self.state,
            json.dumps(self.credential_data),
            self.issued_at.isoformat(),
            self.revoked_at.isoformat() if self.revoked_at else None
        ))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def get_by_exchange_id(cls, credential_exchange_id: str):
        """Get certificate by credential exchange ID"""
        conn = DatabaseManager._get_db_connection()
        row = conn.execute(
            'SELECT * FROM issued_certificates WHERE credential_exchange_id = ?', 
            (credential_exchange_id,)
        ).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_certificates(cls):
        """Get all issued certificates"""
        conn = DatabaseManager._get_db_connection()
        rows = conn.execute(
            'SELECT * FROM issued_certificates ORDER BY issued_at DESC'
        ).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create IssuedCertificateModel from database row"""
        return cls(
            id=row['id'],
            credential_exchange_id=row['credential_exchange_id'],
            connection_id=row['connection_id'],
            user_id=row['user_id'],
            credential_definition_id=row['credential_definition_id'],
            schema_name=row['schema_name'],
            attributes=json.loads(row['attributes']),
            state=row['state'],
            credential_data=json.loads(row['credential_data']) if row['credential_data'] else {},
            issued_at=datetime.fromisoformat(row['issued_at']),
            revoked_at=datetime.fromisoformat(row['revoked_at']) if row['revoked_at'] else None
        )