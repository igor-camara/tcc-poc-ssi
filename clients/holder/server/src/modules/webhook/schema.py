import uuid
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
