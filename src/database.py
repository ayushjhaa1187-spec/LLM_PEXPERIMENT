"""Database configuration and connection management for Phase 1"""
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool, NullPool

from .models import Base

# Database configuration based on environment
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///llm_platform.db'  # Default to SQLite for development
)

def get_database_url():
    """Get appropriate database URL based on environment"""
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        return os.getenv('DATABASE_URL_PROD')
    elif env == 'testing':
        return 'sqlite:///:memory:'
    else:
        return DATABASE_URL

def get_engine():
    """Create and configure database engine"""
    url = get_database_url()
    
    # Common engine options
    engine_opts = {
        'echo': os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true',
        'pool_pre_ping': True,  # Verify connection before using
        'pool_recycle': 3600,   # Recycle connections after 1 hour
    }
    
    # Environment-specific options
    if 'sqlite' in url:
        engine_opts['connect_args'] = {'check_same_thread': False}
        engine_opts['poolclass'] = StaticPool
    elif 'postgresql' in url:
        engine_opts['pool_size'] = 20
        engine_opts['max_overflow'] = 40
        engine_opts['pool_timeout'] = 30
    elif 'mysql' in url:
        engine_opts['pool_size'] = 20
        engine_opts['max_overflow'] = 40
        engine_opts['pool_timeout'] = 30
    
    engine = create_engine(url, **engine_opts)
    
    # Add event listeners for connection management
    @event.listens_for(engine, 'connect')
    def receive_connect(dbapi_conn, connection_record):
        """Configure connection settings on connect"""
        if 'sqlite' in url:
            # Enable foreign keys for SQLite
            cursor = dbapi_conn.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()
    
    return engine

# Create engine and session factory
engine = get_engine()
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

def init_db():
    """Initialize database with all tables"""
    Base.metadata.create_all(engine)

def drop_db():
    """Drop all tables from database"""
    Base.metadata.drop_all(engine)

def get_session():
    """Get a new database session"""
    return Session()

@contextmanager
def session_scope():
    """Provide a transactional scope for database operations"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def close_db(app=None):
    """Close database session on app shutdown"""
    Session.remove()

def configure_app_db(app):
    """Configure Flask app with database"""
    # Initialize database
    init_db()
    
    # Register teardown
    app.teardown_appcontext(lambda exc: close_db(app))

# Connection pool management for high-concurrency scenarios
class ConnectionPoolManager:
    """Manage connection pool for optimal performance"""
    
    @staticmethod
    def get_pool_size():
        """Get recommended pool size based on environment"""
        env = os.getenv('ENVIRONMENT', 'development')
        if env == 'production':
            return 30
        elif env == 'staging':
            return 20
        else:
            return 5
    
    @staticmethod
    def get_pool_overflow():
        """Get recommended overflow size"""
        env = os.getenv('ENVIRONMENT', 'development')
        if env == 'production':
            return 60
        elif env == 'staging':
            return 40
        else:
            return 10
    
    @staticmethod
    def get_pool_timeout():
        """Get pool timeout in seconds"""
        return 30
    
    @staticmethod
    def get_pool_recycle():
        """Get pool recycle interval in seconds"""
        return 3600

def get_db_health():
    """Check database health and connectivity"""
    try:
        connection = engine.connect()
        result = connection.execute('SELECT 1')
        connection.close()
        return {'status': 'healthy', 'connected': True}
    except Exception as e:
        return {'status': 'unhealthy', 'connected': False, 'error': str(e)}
