from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
# In SQLAlchemy 2.0 this should be sqlalchemy.orm.declarative_base but kept for compatibility or updated if needed
# The warning said it is available as sqlalchemy.orm.declarative_base
# Let's try to updating it to sqlalchemy.orm to silence the warning.
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError, OperationalError, DatabaseError
from app.core.config import settings
from app.core.logging_config import get_logger
import os
import time
from functools import wraps

logger = get_logger(__name__)

# Lazy engine creation - only create when needed
_engine = None
_SessionLocal = None

def reset_engine():
    """Reset the database engine (close and clear)"""
    global _engine, _SessionLocal
    if _engine:
        try:
            _engine.dispose()
        except Exception as e:
            logger.warning(f"Error disposing engine: {e}")
    _engine = None
    _SessionLocal = None

def test_connection(engine):
    """Test if database connection is alive"""
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
        return True
    except (DisconnectionError, OperationalError, DatabaseError) as e:
        logger.warning(f"Database connection test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing connection: {e}")
        return False

def reconnect_with_retry(infinite_retry: bool = False):
    """
    Reconnect to database with retry logic and exponential backoff.
    
    Args:
        infinite_retry: If True, retry indefinitely until connection is established.
                       If False, retry up to settings.DB_RECONNECT_RETRIES times.
    """
    global _engine
    retries = settings.DB_RECONNECT_RETRIES
    delay = settings.DB_RECONNECT_DELAY
    
    attempt = 0
    while infinite_retry or attempt < retries:
        try:
            logger.info(f"Attempting to reconnect to database (attempt {attempt + 1}/{'infinite' if infinite_retry else retries})...")
            reset_engine()
            
            _engine = create_engine(
                settings.get_database_url(),
                pool_pre_ping=settings.DB_POOL_PRE_PING,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_recycle=3600,  # Recycle connections after 1 hour
            )
            
            # Test the connection
            if test_connection(_engine):
                logger.info("Database reconnection successful")
                return _engine
            else:
                raise OperationalError("Connection test failed", None, None)
                
        except Exception as e:
            logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")
            
            if infinite_retry or attempt < retries - 1:
                wait_time = delay * (settings.DB_RECONNECT_BACKOFF ** attempt) if not infinite_retry else 5 # Cap delay for infinite or just use fixed/capped backoff
                if infinite_retry:
                    # For infinite retry, use a capped backoff logic, e.g. max 30s
                    wait_time = min(30, delay * (settings.DB_RECONNECT_BACKOFF ** (attempt if attempt < 10 else 10)))

                logger.info(f"Database disconnected. Waiting {wait_time:.2f} seconds for database to come up...")
                time.sleep(wait_time)
                attempt += 1 
            else:
                logger.error(f"Failed to reconnect after {retries} attempts")
                if settings.DEBUG_MODE:
                    logger.warning("Running in debug mode - continuing without database")
                    _engine = None
                    return None
                raise
    
    return _engine

def get_engine(fail_fast: bool = False):
    """
    Get or create database engine with auto-reconnect.
    
    Args:
        fail_fast: If True, do not attempt to reconnect if connection fails/is missing.
                   Used during startup to strictly control retry logic.
    """
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(
                settings.get_database_url(),
                pool_pre_ping=settings.DB_POOL_PRE_PING,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_recycle=3600,  # Recycle connections after 1 hour
            )
            # Test initial connection
            if not test_connection(_engine):
                logger.warning("Initial connection test failed...")
                if fail_fast:
                    _engine = None
                    return None
                
                logger.warning("Attempting reconnect (infinite wait)...")
                _engine = reconnect_with_retry(infinite_retry=True)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            if fail_fast:
                 _engine = None
                 return None
            
            # In debug mode, allow running without database
            if settings.DEBUG_MODE:
                logger.warning("Running in debug mode - continuing without database")
                _engine = None
            else:
                # Try to reconnect indefinitely
                _engine = reconnect_with_retry(infinite_retry=True)
    else:
        # Check if existing connection is still alive
        if not test_connection(_engine):
            logger.warning("Database connection lost...")
            if fail_fast:
                return _engine # Return broken engine? Or None? 
                # If fail_fast is True, we assume the caller checks validity or we return None. 
                # But main.py checks `if engine` then `test_connection`.
                # If we return the stale engine, main.py will test it and fail.
                # Let's clean it.
                _engine = None
                return None

            logger.warning("Attempting to reconnect (wait for DB)...")
            _engine = reconnect_with_retry(infinite_retry=True)
    
    return _engine
    
    return _engine

def get_session_local():
    """Get or create session maker"""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        if engine is None:
            return None
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

Base = declarative_base()

# Export SessionLocal for direct use in scripts
def SessionLocal():
    """Get a database session (for use in scripts) with auto-reconnect"""
    session_maker = get_session_local()
    if session_maker is None:
        # Try to reconnect
        engine = reconnect_with_retry(infinite_retry=True)
        if engine is None:
            if settings.DEBUG_MODE:
                return None
            raise Exception("Database not available")
        session_maker = get_session_local()
        if session_maker is None:
            if settings.DEBUG_MODE:
                return None
            raise Exception("Database not available")
    
    try:
        return session_maker()
    except (DisconnectionError, OperationalError, DatabaseError) as e:
        logger.warning(f"Database session error in SessionLocal: {e}, attempting reconnect...")
        reset_engine()
        global _SessionLocal
        _SessionLocal = None
        session_maker = get_session_local()
        if session_maker:
            return session_maker()
        else:
            if settings.DEBUG_MODE:
                return None
            raise Exception(f"Database reconnection failed: {e}")

def with_reconnect(func):
    """Decorator to automatically reconnect on database errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 2
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (DisconnectionError, OperationalError, DatabaseError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Database error detected, attempting reconnect: {e}")
                    reset_engine()
                    # Force recreation of engine and session
                    global _SessionLocal
                    _SessionLocal = None
                    time.sleep(1)  # Brief pause before retry
                else:
                    logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                # For non-database errors, don't retry
                raise
        return None
    return wrapper

def get_db():
    """Dependency for getting database session with auto-reconnect"""
    session_maker = get_session_local()
    if session_maker is None:
        # In debug mode without DB, return None
        if settings.DEBUG_MODE:
            yield None
            return
        # Try to reconnect
        engine = reconnect_with_retry(infinite_retry=True)
        if engine is None:
            if settings.DEBUG_MODE:
                yield None
                return
            raise Exception("Database not available")
        session_maker = get_session_local()
        if session_maker is None:
            if settings.DEBUG_MODE:
                yield None
                return
            raise Exception("Database not available")
    
    db = None
    try:
        db = session_maker()
        yield db
    except (DisconnectionError, OperationalError, DatabaseError) as e:
        logger.warning(f"Database session error: {e}")
        # Mark engine as possibly stale so next request reconnects
        reset_engine()
        global _SessionLocal
        _SessionLocal = None
        
        # We cannot yield again or retry the request here.
        # Reraise the exception to let FastAPI handle the error (500)
        # and trigger middleware/cleanup.
        raise e
    finally:
        if db:
            try:
                db.close()
            except:
                pass

