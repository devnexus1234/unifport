"""
End-to-end tests for authentication workflows
These tests simulate complete user workflows
"""
import pytest
from fastapi import status
from app.models.user import User
from app.models.rbac import Role, UserRole
from app.core.security import create_access_token, create_refresh_token


@pytest.mark.e2e
class TestAuthE2E:
    """End-to-end tests for authentication"""
    
    def test_complete_login_and_access_flow(self, client, test_db):
        """Test complete flow: login -> get user info -> access protected endpoint"""
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
        
        # Step 1: Login
        with pytest.MonkeyPatch().context() as m:
            from app.api.v1 import auth
            m.setattr(auth, 'authenticate_ldap', lambda u, p: True)
            m.setattr(auth, 'get_user_groups_ldap', lambda u: ["users"])
            
            login_response = client.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "password"}
            )
            
            assert login_response.status_code == status.HTTP_200_OK
            login_data = login_response.json()
            access_token = login_data["access_token"]
            refresh_token = login_data["refresh_token"]
            
            # Step 2: Get current user info
            me_response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert me_response.status_code == status.HTTP_200_OK
            me_data = me_response.json()
            assert me_data["username"] == "testuser"
            
            # Step 3: Refresh token
            refresh_response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            assert refresh_response.status_code == status.HTTP_200_OK
            refresh_data = refresh_response.json()
            new_access_token = refresh_data["access_token"]
            
            # Step 4: Use new token to access protected endpoint
            me_response2 = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {new_access_token}"}
            )
            
            assert me_response2.status_code == status.HTTP_200_OK
    
    def test_login_with_role_assignment(self, client, test_db):
        """Test login flow with role assignment"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create role
        role = Role(name="User")
        test_db.add(role)
        test_db.commit()
        test_db.refresh(role)
        
        # Assign role to user
        user_role = UserRole(user_id=user.id, role_id=role.id)
        test_db.add(user_role)
        test_db.commit()
        
        # Login
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
            assert "User" in data["user"]["roles"]
    
    def test_token_expiration_and_refresh_flow(self, client, test_db):
        """Test token expiration and refresh workflow"""
        user = User(
            username="testuser",
            email="test@example.com",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create refresh token manually
        refresh_token = create_refresh_token({"sub": user.username, "user_id": user.id})
        
        # Use refresh token to get new access token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        new_access_token = data["access_token"]
        
        # Use new access token
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        
        assert me_response.status_code == status.HTTP_200_OK

