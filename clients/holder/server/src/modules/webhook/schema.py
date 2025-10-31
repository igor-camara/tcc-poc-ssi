import uuid
import json
import sqlite3
from datetime import datetime
from modules.config.settings import settings


class Notification:
    """Notification model for webhook events"""
    
    def __init__(self, tipo=None, connection_id=None, id=None, read=False, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.tipo = tipo
        self.connection_id = connection_id
        self.read = read
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @staticmethod
    def _get_db_connection():
        """Get database connection"""
        db_path = settings.database_url.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def init_db():
        """Initialize database tables"""
        conn = Notification._get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                connection_id TEXT,
                read NUMBER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_notifications_tipo ON notifications(tipo)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_notifications_connection_id ON notifications(connection_id)')
        conn.commit()
        conn.close()
    
    def __repr__(self):
        return f'<Notification {self.tipo}>'
    
    def to_dict(self):
        """Convert notification object to dictionary"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'connection_id': self.connection_id,
            'read': self.read,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def find_by_id(cls, notification_id):
        """Find notification by ID"""
        conn = cls._get_db_connection()
        row = conn.execute('SELECT * FROM notifications WHERE id = ?', (notification_id,)).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
       
    @classmethod
    def find_by_connection_id(cls, connection_id):
        """Find notifications by connection ID"""
        conn = cls._get_db_connection()
        rows = conn.execute('SELECT * FROM notifications WHERE connection_id = ? ORDER BY created_at DESC', 
                          (connection_id,)).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def find_all(cls, limit=100):
        """Find all notifications"""
        conn = cls._get_db_connection()
        rows = conn.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?', 
                          (limit,)).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create Notification instance from database row"""
        created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow()
        updated_at = datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.utcnow()
        
        notification = cls(
            id=row['id'],
            tipo=row['tipo'],
            connection_id=row['connection_id'],
            read=bool(row['read']),
            created_at=created_at,
            updated_at=updated_at
        )
        
        return notification
    
    def save(self):
        """Save notification to database"""
        conn = self._get_db_connection()
        try:
            self.updated_at = datetime.utcnow()
            
            existing = conn.execute('SELECT id FROM notifications WHERE id = ?', (self.id,)).fetchone()
            
            if existing:
                # Update
                conn.execute('''
                    UPDATE notifications SET 
                        tipo = ?, connection_id = ?, read = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    self.tipo, self.connection_id, int(self.read), self.updated_at.isoformat(), self.id
                ))
            else:
                # Insert
                conn.execute('''
                    INSERT INTO notifications 
                    (id, tipo, connection_id, read, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    self.id, self.tipo, self.connection_id, int(self.read),
                    self.created_at.isoformat(), self.updated_at.isoformat()
                ))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


class CredentialOffer:
    """Credential Offer model for storing credential preview data"""
    
    def __init__(self, cred_ex_id=None, connection_id=None, state=None, 
                 credential_preview=None, schema_id=None, cred_def_id=None,
                 created_at=None, updated_at=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.cred_ex_id = cred_ex_id
        self.connection_id = connection_id
        self.state = state
        self.credential_preview = credential_preview or []
        self.schema_id = schema_id
        self.cred_def_id = cred_def_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @staticmethod
    def _get_db_connection():
        """Get database connection"""
        db_path = settings.database_url.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def init_db():
        """Initialize database tables"""
        conn = CredentialOffer._get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS credential_offers (
                id TEXT PRIMARY KEY,
                cred_ex_id TEXT NOT NULL UNIQUE,
                connection_id TEXT,
                state TEXT NOT NULL,
                credential_preview TEXT,
                schema_id TEXT,
                cred_def_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_credential_offers_cred_ex_id ON credential_offers(cred_ex_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_credential_offers_connection_id ON credential_offers(connection_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_credential_offers_state ON credential_offers(state)')
        conn.commit()
        conn.close()
    
    def __repr__(self):
        return f'<CredentialOffer {self.cred_ex_id}>'
    
    def to_dict(self):
        """Convert credential offer object to dictionary"""
        return {
            'id': self.id,
            'cred_ex_id': self.cred_ex_id,
            'connection_id': self.connection_id,
            'state': self.state,
            'credential_preview': self.credential_preview if isinstance(self.credential_preview, list) else json.loads(self.credential_preview) if self.credential_preview else [],
            'schema_id': self.schema_id,
            'cred_def_id': self.cred_def_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def find_by_id(cls, offer_id):
        """Find credential offer by ID"""
        conn = cls._get_db_connection()
        row = conn.execute('SELECT * FROM credential_offers WHERE id = ?', (offer_id,)).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_cred_ex_id(cls, cred_ex_id):
        """Find credential offer by credential exchange ID"""
        conn = cls._get_db_connection()
        row = conn.execute('SELECT * FROM credential_offers WHERE cred_ex_id = ?', (cred_ex_id,)).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_connection_id(cls, connection_id):
        """Find credential offers by connection ID"""
        conn = cls._get_db_connection()
        rows = conn.execute('SELECT * FROM credential_offers WHERE connection_id = ? ORDER BY created_at DESC', 
                          (connection_id,)).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def find_all(cls, limit=100):
        """Find all credential offers"""
        conn = cls._get_db_connection()
        rows = conn.execute('SELECT * FROM credential_offers ORDER BY created_at DESC LIMIT ?', 
                          (limit,)).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create CredentialOffer instance from database row"""
        created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow()
        updated_at = datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.utcnow()
        
        offer = cls(
            id=row['id'],
            cred_ex_id=row['cred_ex_id'],
            connection_id=row['connection_id'],
            state=row['state'],
            credential_preview=json.loads(row['credential_preview']) if row['credential_preview'] else [],
            schema_id=row['schema_id'],
            cred_def_id=row['cred_def_id'],
            created_at=created_at,
            updated_at=updated_at
        )
        
        return offer
    
    def save(self):
        """Save credential offer to database"""
        conn = self._get_db_connection()
        try:
            self.updated_at = datetime.utcnow()
            
            existing = conn.execute('SELECT id FROM credential_offers WHERE cred_ex_id = ?', (self.cred_ex_id,)).fetchone()
            
            credential_preview_json = json.dumps(self.credential_preview) if isinstance(self.credential_preview, list) else self.credential_preview
            
            created_at_str = self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
            updated_at_str = self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
            
            if existing:
                # Update
                conn.execute('''
                    UPDATE credential_offers SET 
                        connection_id = ?, state = ?, credential_preview = ?, 
                        schema_id = ?, cred_def_id = ?, updated_at = ?
                    WHERE cred_ex_id = ?
                ''', (
                    self.connection_id, self.state, credential_preview_json,
                    self.schema_id, self.cred_def_id, updated_at_str, self.cred_ex_id
                ))
            else:
                # Insert
                conn.execute('''
                    INSERT INTO credential_offers 
                    (id, cred_ex_id, connection_id, state, credential_preview, 
                     schema_id, cred_def_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.id, self.cred_ex_id, self.connection_id, self.state,
                    credential_preview_json, self.schema_id, self.cred_def_id,
                    created_at_str, updated_at_str
                ))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


class PresentProofRequest:
    def __init__(self, pres_ex_id=None, state=None, name=None, version=None, 
                 requested_attributes=None, requested_predicates=None, 
                 created_at=None, updated_at=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.pres_ex_id = pres_ex_id
        self.state = state
        self.name = name
        self.version = version
        self.requested_attributes = requested_attributes or {}
        self.requested_predicates = requested_predicates or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @staticmethod
    def _get_db_connection():
        db_path = settings.database_url.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def init_db():
        conn = PresentProofRequest._get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS present_proof_requests (
                id TEXT PRIMARY KEY,
                pres_ex_id TEXT NOT NULL UNIQUE,
                state TEXT NOT NULL,
                name TEXT,
                version TEXT,
                requested_attributes TEXT,
                requested_predicates TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_present_proof_requests_pres_ex_id ON present_proof_requests(pres_ex_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_present_proof_requests_state ON present_proof_requests(state)')
        conn.commit()
        conn.close()
    
    def __repr__(self):
        return f'<PresentProofRequest {self.pres_ex_id}>'
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'pres_ex_id': self.pres_ex_id,
            'state': self.state,
            'name': self.name,
            'version': self.version,
            'requested_attributes': self.requested_attributes if isinstance(self.requested_attributes, dict) else json.loads(self.requested_attributes) if self.requested_attributes else {},
            'requested_predicates': self.requested_predicates if isinstance(self.requested_predicates, dict) else json.loads(self.requested_predicates) if self.requested_predicates else {},
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def find_by_id(cls, proof_id):
        conn = cls._get_db_connection()
        row = conn.execute('SELECT * FROM present_proof_requests WHERE id = ?', (proof_id,)).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_pres_ex_id(cls, pres_ex_id):
        conn = cls._get_db_connection()
        row = conn.execute('SELECT * FROM present_proof_requests WHERE pres_ex_id = ?', (pres_ex_id,)).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_all(cls, limit=100):
        conn = cls._get_db_connection()
        rows = conn.execute('SELECT * FROM present_proof_requests ORDER BY created_at DESC LIMIT ?', 
                          (limit,)).fetchall()
        conn.close()
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow()
        updated_at = datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.utcnow()
        
        proof_request = cls(
            id=row['id'],
            pres_ex_id=row['pres_ex_id'],
            state=row['state'],
            name=row['name'],
            version=row['version'],
            requested_attributes=json.loads(row['requested_attributes']) if row['requested_attributes'] else {},
            requested_predicates=json.loads(row['requested_predicates']) if row['requested_predicates'] else {},
            created_at=created_at,
            updated_at=updated_at
        )
        
        return proof_request
    
    def save(self):
        conn = self._get_db_connection()
        try:
            self.updated_at = datetime.utcnow()
            
            existing = conn.execute('SELECT id FROM present_proof_requests WHERE pres_ex_id = ?', (self.pres_ex_id,)).fetchone()
            
            requested_attributes_json = json.dumps(self.requested_attributes) if isinstance(self.requested_attributes, dict) else self.requested_attributes
            requested_predicates_json = json.dumps(self.requested_predicates) if isinstance(self.requested_predicates, dict) else self.requested_predicates
            
            created_at_str = self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
            updated_at_str = self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
            
            if existing:
                # Update
                conn.execute('''
                    UPDATE present_proof_requests SET 
                        state = ?, name = ?, version = ?, 
                        requested_attributes = ?, requested_predicates = ?, 
                        updated_at = ?
                    WHERE pres_ex_id = ?
                ''', (
                    self.state, self.name, self.version,
                    requested_attributes_json, requested_predicates_json,
                    updated_at_str, self.pres_ex_id
                ))
            else:
                # Insert
                conn.execute('''
                    INSERT INTO present_proof_requests 
                    (id, pres_ex_id, state, name, version, requested_attributes, 
                     requested_predicates, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.id, self.pres_ex_id, self.state, self.name, self.version,
                    requested_attributes_json, requested_predicates_json,
                    created_at_str, updated_at_str
                ))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
