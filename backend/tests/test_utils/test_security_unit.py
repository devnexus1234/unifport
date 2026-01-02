"""
Unit tests for security functions
"""
import pytest
from datetime import timedelta
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.core.config import settings


@pytest.mark.unit
class TestSecurityUnit:
    """Unit tests for security utilities"""
    

    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "testuser", "user_id": 1}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_success(self):
        """Test token verification with valid token"""
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)
        
        payload = verify_token(token, token_type="access")
        
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 1
    
    def test_verify_token_wrong_type(self):
        """Test token verification with wrong token type"""
        data = {"sub": "testuser", "user_id": 1}
        access_token = create_access_token(data)
        
        # Try to verify access token as refresh token
        payload = verify_token(access_token, token_type="refresh")
        
        assert payload is None
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        payload = verify_token("invalid_token_string", token_type="access")
        
        assert payload is None
    
    def test_token_expiration(self):
        """Test token expiration"""
        data = {"sub": "testuser", "user_id": 1}
        # Create token with very short expiration
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        payload = verify_token(token, token_type="access")
        
        # Token should be expired
        assert payload is None

