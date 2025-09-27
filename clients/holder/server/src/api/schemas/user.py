import uuid
import sqlite3
import os
from datetime import datetime
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    """User model for authentication"""
    
    def __init__(self, email=None, password=None, first_name=None, last_name=None, 
                 id=None, did=None, verkey=None, 
                 is_active=True, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.email = email.lower() if email else None
        self.password_hash = None
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active
        self.did = did
        self.verkey = verkey
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        if password:
            self.set_password(password)
    
    @staticmethod
    def _get_db_connection():
        """Get database connection"""
        db_path = os.environ.get('DATABASE_URL', 'sqlite:///holder.db').replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def init_db():
        """Initialize database tables"""
        conn = User._get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                is_active INTEGER DEFAULT 1,
                did TEXT UNIQUE,
                verkey TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_users_did ON users(did)')
        conn.commit()
        conn.close()
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = pwd_context.hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return pwd_context.verify(password, self.password_hash)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'did': self.did,
            'verkey': self.verkey,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        conn = cls._get_db_connection()
        row = conn.execute('SELECT * FROM users WHERE email = ?', (email.lower(),)).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        conn = cls._get_db_connection()
        row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def _from_row(cls, row):
        """Create User instance from database row"""
        import json
        
        created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.utcnow()
        updated_at = datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.utcnow()
        
        user = cls(
            id=row['id'],
            email=row['email'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            is_active=bool(row['is_active']),
            did=row['did'],
            verkey=row['verkey'],
            created_at=created_at,
            updated_at=updated_at
        )
        user.password_hash = row['password_hash']
        return user
    
    def save(self):
        """Save user to database"""
        import json
        
        conn = self._get_db_connection()
        try:
            self.updated_at = datetime.utcnow()
            
            # Check if user exists
            existing = conn.execute('SELECT id FROM users WHERE id = ?', (self.id,)).fetchone()
            
            if existing:
                # Update
                conn.execute('''
                    UPDATE users SET 
                        email = ?, password_hash = ?, first_name = ?, last_name = ?,
                        is_active = ?, did = ?, verkey = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    self.email, self.password_hash, self.first_name, self.last_name,
                    int(self.is_active), self.did, self.verkey, self.updated_at.isoformat(), self.id
                ))
            else:
                # Insert
                conn.execute('''
                    INSERT INTO users 
                    (id, email, password_hash, first_name, last_name, is_active, 
                     did, verkey, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.id, self.email, self.password_hash, self.first_name, self.last_name,
                    int(self.is_active), self.did, self.verkey, self.created_at.isoformat(), self.updated_at.isoformat()
                ))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete(self):
        """Delete user from database"""
        conn = self._get_db_connection()
        try:
            conn.execute('DELETE FROM users WHERE id = ?', (self.id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()