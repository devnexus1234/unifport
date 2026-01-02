"""
Integration tests for authentication endpoints
These tests use a real test database
"""
import pytest
from fastapi import status
from app.models.user import User
from app.models.rbac import Role, UserRole
from app.core.security import create_access_token, create_refresh_token


@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests for authentication"""
    
    def test_login_flow(self, client, test_db):
        """Test complete login flow with database"""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            is_admin=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Mock LDAP authentication
        with pytest.MonkeyPatch().context() as m:
            from app.api.v1 import auth
            m.setattr(auth, 'authenticate_ldap', lambda u, p: True)
            m.setattr(auth, 'get_user_groups_ldap', lambda u: ["users"])
            
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "password"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["username"] == "testuser"
    
    def test_login_invalid_credentials(self, client, test_db):
        """Test login with invalid credentials"""
        with pytest.MonkeyPatch().context() as m:
            from app.api.v1 import auth
            m.setattr(auth, 'authenticate_ldap', lambda u, p: False)
            
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "wrongpassword"}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_user_not_found(self, client, test_db):
        """Test login when user doesn't exist"""
        with pytest.MonkeyPatch().context() as m:
            from app.api.v1 import auth
            m.setattr(auth, 'authenticate_ldap', lambda u, p: True)
            
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "nonexistent", "password": "password"}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_flow(self, client, test_db):
        """Test token refresh flow"""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create refresh token
        refresh_token = create_refresh_token({"sub": user.username, "user_id": user.id})
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_get_current_user(self, client, test_db):
        """Test getting current user info"""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            is_admin=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_inactive(self, client, test_db):
        """Test getting current user when user is inactive"""
        # Create inactive user
        user = User(
            username="inactive",
            email="inactive@example.com",
            is_active=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

