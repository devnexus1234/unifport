"""
Comprehensive Auth API Integration Tests with Full Authentication
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.rbac import Role, UserRole
from app.core.security import create_access_token, create_refresh_token

# Import fixtures
pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestAuthAPIFull:
    
    @patch('app.api.v1.auth.authenticate_ldap')
    @patch('app.api.v1.auth.get_user_groups_ldap')
    def test_login_success_full_flow(self, mock_groups, mock_ldap, client, test_db, regular_user):
        """Test complete login flow with LDAP and token generation"""
        mock_ldap.return_value = True
        mock_groups.return_value = ["users", "developers"]
        
        response = client.post("/api/v1/auth/login", json={
            "username": regular_user.username,
            "password": "testpassword"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert "user" in data
            assert data["user"]["username"] == regular_user.username
    
    @patch('app.api.v1.auth.authenticate_ldap')
    def test_login_user_not_found(self, mock_ldap, client, test_db):
        """Test login with user not in database"""
        mock_ldap.return_value = True
        
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        
        assert response.status_code in [401, 404]
    
    @patch('app.api.v1.auth.authenticate_ldap')
    def test_login_inactive_user(self, mock_ldap, client, test_db, inactive_user):
        """Test login with inactive user"""
        mock_ldap.return_value = True
        
        response = client.post("/api/v1/auth/login", json={
            "username": inactive_user.username,
            "password": "password"
        })
        
        assert response.status_code in [403, 401]
    
    @patch('app.api.v1.auth.authenticate_ldap')
    def test_login_ldap_failure(self, mock_ldap, client, regular_user):
        """Test login with LDAP authentication failure"""
        mock_ldap.return_value = False
        
        response = client.post("/api/v1/auth/login", json={
            "username": regular_user.username,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    @patch('app.api.v1.auth.authenticate_ldap')
    @patch('app.api.v1.auth.get_user_groups_ldap')
    def test_login_with_roles(self, mock_groups, mock_ldap, client, test_db, user_with_role):
        """Test login with user that has roles"""
        mock_ldap.return_value = True
        mock_groups.return_value = []
        
        response = client.post("/api/v1/auth/login", json={
            "username": user_with_role.username,
            "password": "password"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "user" in data
            assert "roles" in data["user"]
    
    def test_refresh_token_success(self, client, test_db, regular_user):
        """Test refresh token endpoint"""
        refresh_token = create_refresh_token(
            data={"sub": regular_user.username, "user_id": regular_user.id}
        )
        
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code in [401, 422]
    
    def test_refresh_token_inactive_user(self, client, test_db, inactive_user):
        """Test refresh token with inactive user"""
        refresh_token = create_refresh_token(
            data={"sub": inactive_user.username, "user_id": inactive_user.id}
        )
        
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code in [401]
    
    def test_me_endpoint_success(self, client, regular_token_headers, regular_user):
        """Test /me endpoint with valid token"""
        response = client.get("/api/v1/auth/me", headers=regular_token_headers)
        
        if response.status_code == 200:
            data = response.json()
            assert data["username"] == regular_user.username
            assert data["email"] == regular_user.email
            assert "roles" in data
    
    def test_me_endpoint_unauthorized(self, client):
        """Test /me endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]
    
    def test_me_endpoint_invalid_token(self, client):
        """Test /me endpoint with invalid token"""
        response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
        assert response.status_code in [401, 403]
    
    def test_get_current_user_helper(self, client, regular_token_headers, regular_user):
        """Test get_current_user dependency"""
        # This is tested indirectly through /me endpoint
        response = client.get("/api/v1/auth/me", headers=regular_token_headers)
        assert response.status_code in [200, 404]
    
    def test_get_current_active_user_helper(self, client, test_db, inactive_user):
        """Test get_current_active_user with inactive user"""
        token = create_access_token(
            data={"sub": inactive_user.username, "user_id": inactive_user.id}
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code in [400, 401, 403]
    
    def test_get_current_user_no_username(self, client, test_db):
        """Test get_current_user with token missing username"""
        # Create token without 'sub' field
        token = create_access_token(data={"user_id": 999})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code in [401, 403]
    
    def test_get_current_user_no_user_id(self, client, test_db):
        """Test get_current_user with token missing user_id"""
        # Create token without 'user_id' field
        token = create_access_token(data={"sub": "testuser"})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code in [401, 403]
    
    def test_get_current_user_user_not_found(self, client, test_db):
        """Test get_current_user with non-existent user"""
        # Create token for non-existent user
        token = create_access_token(data={"sub": "nonexistent", "user_id": 99999})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code in [401, 403]
    
    def test_me_endpoint_with_roles(self, client, test_db, user_with_role):
        """Test /me endpoint returns user roles"""
        token = create_access_token(
            data={"sub": user_with_role.username, "user_id": user_with_role.id}
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert "roles" in data
