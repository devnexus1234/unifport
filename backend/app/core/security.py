from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.time_utils import get_ist_time

# LDAP import - optional in debug mode
try:
    import ldap
    LDAP_AVAILABLE = True
except ImportError:
    LDAP_AVAILABLE = False
    if not settings.DEBUG_MODE:
        raise ImportError("python-ldap is required when DEBUG_MODE is False")

from app.core.config import settings as app_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = get_ist_time() + expires_delta
    else:
        expire = get_ist_time() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": get_ist_time(),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = get_ist_time() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": get_ist_time(),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            return None
        
        return payload
    except JWTError:
        return None

def authenticate_ldap(username: str, password: str) -> bool:
    """Authenticate user against LDAP"""
    if app_settings.DEBUG_MODE:
        # In debug mode, bypass LDAP authentication
        return True
    
    if not LDAP_AVAILABLE:
        # If LDAP not available and not in debug mode, fail
        if not app_settings.DEBUG_MODE:
            return False
        return True
    
    try:
        conn = ldap.initialize(app_settings.LDAP_SERVER)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.protocol_version = ldap.VERSION3
        
        user_dn = f"uid={username},{app_settings.LDAP_USER_DN}"
        conn.simple_bind_s(user_dn, password)
        conn.unbind()
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except Exception as e:
        print(f"LDAP authentication error: {e}")
        return False

def get_user_groups_ldap(username: str) -> list:
    """Get user groups from LDAP"""
    if app_settings.DEBUG_MODE:
        # In debug mode, return default groups
        return ["admin", "users"]
    
    if not LDAP_AVAILABLE:
        # If LDAP not available, return default groups in debug mode
        if app_settings.DEBUG_MODE:
            return ["admin", "users"]
        return []
    
    try:
        conn = ldap.initialize(app_settings.LDAP_SERVER)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.protocol_version = ldap.VERSION3
        conn.simple_bind_s(app_settings.LDAP_USER_DN, "")
        
        search_filter = f"(uid={username})"
        result = conn.search_s(
            app_settings.LDAP_BASE_DN,
            ldap.SCOPE_SUBTREE,
            search_filter,
            ["memberOf"]
        )
        
        groups = []
        if result:
            for dn, attrs in result:
                if 'memberOf' in attrs:
                    groups = [group.decode('utf-8') for group in attrs['memberOf']]
        
        conn.unbind()
        return groups
    except Exception as e:
        print(f"LDAP group lookup error: {e}")
        return []

