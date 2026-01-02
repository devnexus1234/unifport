"""
Tests for Security Module
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    authenticate_ldap,
    get_user_groups_ldap
)

@pytest.mark.unit
class TestPasswordHashing:
    @patch('app.core.security.pwd_context')
    def test_password_hash_and_verify(self, mock_pwd_context):
        """Test password hashing and verification"""
        mock_pwd_context.hash.return_value = "hashed_password"
        mock_pwd_context.verify.return_value = True
        
        password = "testpass"
        hashed = get_password_hash(password)
        
        assert hashed == "hashed_password"
        assert verify_password(password, hashed) is True
    
    @patch('app.core.security.pwd_context')
    def test_verify_wrong_password(self, mock_pwd_context):
        """Test verification with wrong password"""
        mock_pwd_context.hash.return_value = "hashed_password"
        mock_pwd_context.verify.return_value = False
        
        password = "correct"
        wrong_password = "wrong"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False


@pytest.mark.unit
class TestJWTTokens:
    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        
        # Verify token contains expected data
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify it's a refresh token
        payload = verify_token(token, token_type="refresh")
        assert payload is not None
        assert payload["type"] == "refresh"
    
    def test_verify_valid_token(self):
        """Test verifying valid token"""
        data = {"sub": "testuser", "email": "test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["email"] == "test@example.com"
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_wrong_token_type(self):
        """Test verifying token with wrong type"""
        data = {"sub": "testuser"}
        access_token = create_access_token(data)
        
        # Try to verify as refresh token
        payload = verify_token(access_token, token_type="refresh")
        assert payload is None


@pytest.mark.unit
class TestLDAPAuthentication:
    def test_authenticate_ldap_debug_mode(self):
        """Test LDAP authentication in debug mode"""
        with patch('app.core.security.app_settings') as mock_settings:
            mock_settings.DEBUG_MODE = True
            
            result = authenticate_ldap("testuser", "password")
            assert result is True
    
    @patch('app.core.security.LDAP_AVAILABLE', True)
    @patch('app.core.security.ldap', create=True)
    def test_authenticate_ldap_success(self, mock_ldap):
        """Test successful LDAP authentication"""
        mock_conn = MagicMock()
        mock_ldap.initialize.return_value = mock_conn
        
        with patch('app.core.security.app_settings') as mock_settings:
            mock_settings.DEBUG_MODE = False
            mock_settings.LDAP_SERVER = "ldap://test.server"
            mock_settings.LDAP_USER_DN = "ou=users,dc=example,dc=com"
            
            result = authenticate_ldap("testuser", "password")
            assert result is True
            mock_conn.simple_bind_s.assert_called_once()
            mock_conn.unbind.assert_called_once()
    
    @patch('app.core.security.LDAP_AVAILABLE', True)
    @patch('app.core.security.ldap', create=True)
    def test_authenticate_ldap_invalid_credentials(self, mock_ldap):
        """Test LDAP authentication with invalid credentials"""
        mock_conn = MagicMock()
        mock_ldap.initialize.return_value = mock_conn
        mock_ldap.INVALID_CREDENTIALS = Exception
        mock_conn.simple_bind_s.side_effect = mock_ldap.INVALID_CREDENTIALS
        
        with patch('app.core.security.app_settings') as mock_settings:
            mock_settings.DEBUG_MODE = False
            mock_settings.LDAP_SERVER = "ldap://test.server"
            mock_settings.LDAP_USER_DN = "ou=users,dc=example,dc=com"
            
            result = authenticate_ldap("testuser", "wrongpassword")
            assert result is False
    
    def test_get_user_groups_debug_mode(self):
        """Test getting user groups in debug mode"""
        with patch('app.core.security.app_settings') as mock_settings:
            mock_settings.DEBUG_MODE = True
            
            groups = get_user_groups_ldap("testuser")
            assert "admin" in groups
            assert "users" in groups
    
    @patch('app.core.security.LDAP_AVAILABLE', True)
    @patch('app.core.security.ldap', create=True)
    def test_get_user_groups_success(self, mock_ldap):
        """Test getting user groups from LDAP"""
        mock_conn = MagicMock()
        mock_ldap.initialize.return_value = mock_conn
        mock_ldap.SCOPE_SUBTREE = 2
        
        # Mock LDAP search result
        mock_conn.search_s.return_value = [
            ("uid=testuser,ou=users,dc=example,dc=com", {
                "memberOf": [b"cn=admin,ou=groups,dc=example,dc=com"]
            })
        ]
        
        with patch('app.core.security.app_settings') as mock_settings:
            mock_settings.DEBUG_MODE = False
            mock_settings.LDAP_SERVER = "ldap://test.server"
            mock_settings.LDAP_BASE_DN = "dc=example,dc=com"
            mock_settings.LDAP_USER_DN = "ou=users,dc=example,dc=com"
            
            groups = get_user_groups_ldap("testuser")
            assert len(groups) > 0
            mock_conn.unbind.assert_called_once()
    
    @patch('app.core.security.LDAP_AVAILABLE', True)
    @patch('app.core.security.ldap', create=True)
    def test_get_user_groups_error(self, mock_ldap):
        """Test getting user groups with error"""
        mock_ldap.initialize.side_effect = Exception("LDAP error")
        
        with patch('app.core.security.app_settings') as mock_settings:
            mock_settings.DEBUG_MODE = False
            mock_settings.LDAP_SERVER = "ldap://test.server"
            
            groups = get_user_groups_ldap("testuser")
            assert groups == []
