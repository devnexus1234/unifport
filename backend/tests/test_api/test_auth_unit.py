"""
Unit tests for authentication endpoints
These tests mock database and external dependencies
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import status, HTTPException
from app.api.v1.auth import login, refresh_token, get_current_user, get_current_active_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest


@pytest.mark.unit
class TestAuthUnit:
    """Unit tests for authentication endpoints"""
    
    @pytest.mark.asyncio
    @patch('app.api.v1.auth.authenticate_ldap')
    @patch('app.api.v1.auth.get_user_groups_ldap')
    @patch('app.api.v1.auth.create_access_token')
    @patch('app.api.v1.auth.create_refresh_token')
    async def test_login_success(self, mock_refresh_token, mock_access_token, mock_get_groups, mock_authenticate, db_session):
        """Test successful login"""
        # Setup mocks
        mock_authenticate.return_value = True
        mock_get_groups.return_value = ["admin", "users"]
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_123"
        
        # Create test user
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        # Mock database query
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = user
            mock_query.return_value.filter.return_value.all.return_value = []
            
            login_data = LoginRequest(username="testuser", password="password")
            result = await login(login_data, db_session)
            
            assert result["access_token"] == "access_token_123"
            assert result["refresh_token"] == "refresh_token_123"
            assert result["token_type"] == "bearer"
            assert result["user"]["username"] == "testuser"
            mock_authenticate.assert_called_once_with("testuser", "password")
    
    @pytest.mark.asyncio
    @patch('app.api.v1.auth.authenticate_ldap')
    async def test_login_invalid_credentials(self, mock_authenticate, db_session):
        """Test login with invalid credentials"""
        mock_authenticate.return_value = False
        
        login_data = LoginRequest(username="testuser", password="wrongpassword")
        
        with pytest.raises(HTTPException):
            await login(login_data, db_session)
        
        mock_authenticate.assert_called_once_with("testuser", "wrongpassword")
    
    @pytest.mark.asyncio
    @patch('app.api.v1.auth.authenticate_ldap')
    async def test_login_user_not_found(self, mock_authenticate, db_session):
        """Test login when user doesn't exist in database"""
        mock_authenticate.return_value = True
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            login_data = LoginRequest(username="nonexistent", password="password")
            
            with pytest.raises(HTTPException):
                await login(login_data, db_session)
    
    @pytest.mark.asyncio
    @patch('app.api.v1.auth.verify_token')
    @patch('app.api.v1.auth.create_access_token')
    @patch('app.api.v1.auth.create_refresh_token')
    async def test_refresh_token_success(self, mock_refresh_token, mock_access_token, mock_verify, db_session):
        """Test successful token refresh"""
        # Setup mocks
        mock_verify.return_value = {"sub": "testuser", "user_id": 1}
        mock_access_token.return_value = "new_access_token"
        mock_refresh_token.return_value = "new_refresh_token"
        
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=True
        )
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = user
            mock_query.return_value.filter.return_value.all.return_value = []
            
            refresh_data = RefreshTokenRequest(refresh_token="old_refresh_token")
            result = await refresh_token(refresh_data, db_session)
            
            assert result["access_token"] == "new_access_token"
            assert result["refresh_token"] == "new_refresh_token"
            mock_verify.assert_called_once_with("old_refresh_token", token_type="refresh")
    
    @pytest.mark.asyncio
    @patch('app.api.v1.auth.verify_token')
    async def test_refresh_token_invalid(self, mock_verify, db_session):
        """Test refresh with invalid token"""
        mock_verify.return_value = None
        
        refresh_data = RefreshTokenRequest(refresh_token="invalid_token")
        
        with pytest.raises(HTTPException):
            await refresh_token(refresh_data, db_session)
    
    @patch('app.api.v1.auth.verify_token')
    def test_get_current_user_success(self, mock_verify, db_session):
        """Test getting current user from token"""
        mock_verify.return_value = {"sub": "testuser", "user_id": 1}
        
        user = User(id=1, username="testuser", is_active=True)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = user
            
            result = get_current_user(token="valid_token", db=db_session)
            
            assert result.id == 1
            assert result.username == "testuser"
    
    @patch('app.api.v1.auth.verify_token')
    def test_get_current_user_invalid_token(self, mock_verify, db_session):
        """Test getting current user with invalid token"""
        mock_verify.return_value = None
        
        with pytest.raises(HTTPException):
            get_current_user(token="invalid_token", db=db_session)
    
    def test_get_current_active_user_inactive(self, db_session):
        """Test getting current user when user is inactive"""
        user = User(id=1, username="testuser", is_active=False)
        
        with pytest.raises(HTTPException):
            get_current_active_user(current_user=user)

