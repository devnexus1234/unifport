"""
Unit tests for RBAC utility functions
"""
import pytest
from unittest.mock import Mock, patch
from app.utils.rbac import is_admin_user
from app.models.user import User
from app.models.rbac import UserRole, Role


@pytest.mark.unit
class TestRBACUnit:
    """Unit tests for RBAC utilities"""
    
    def test_is_admin_user_flag(self, db_session):
        """Test admin check via is_admin flag"""
        user = User(id=1, username="admin", is_admin=True)
        
        result = is_admin_user(user, db_session)
        
        assert result is True
    
    def test_is_admin_user_role(self, db_session):
        """Test admin check via Admin role"""
        user = User(id=1, username="admin", is_admin=False)
        role = Role(id=1, name="Admin")
        user_role = UserRole(user_id=1, role_id=1)
        
        with patch.object(db_session, 'query') as mock_query:
            # Mock UserRole query
            mock_query.return_value.filter.return_value.all.return_value = [user_role]
            # Mock Role query
            mock_query.return_value.filter.return_value.first.return_value = role
            
            result = is_admin_user(user, db_session)
            
            assert result is True
    
    def test_is_admin_user_not_admin(self, db_session):
        """Test admin check for non-admin user"""
        user = User(id=1, username="user", is_admin=False)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = []
            
            result = is_admin_user(user, db_session)
            
            assert result is False
    
    def test_is_admin_user_no_roles(self, db_session):
        """Test admin check for user with no roles"""
        user = User(id=1, username="user", is_admin=False)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = []
            
            result = is_admin_user(user, db_session)
            
            assert result is False

