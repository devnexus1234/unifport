"""
Unit tests for catalogue endpoints
These tests mock database and external dependencies
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import status, HTTPException
from app.api.v1.catalogues import get_catalogues, get_catalogue, check_catalogue_permission
from app.models.user import User
from app.models.catalogue import Catalogue


@pytest.mark.unit
class TestCataloguesUnit:
    """Unit tests for catalogue endpoints"""
    
    @pytest.mark.asyncio
    @patch('app.api.v1.catalogues.check_catalogue_permission')
    async def test_get_catalogues_success(self, mock_check_permission, db_session):
        """Test getting all catalogues"""
        user = User(id=1, username="testuser", is_active=True)
        
        catalogue1 = Catalogue(
            id=1,
            name="Catalogue 1",
            is_enabled=True,
            is_active=True,
            display_order=1
        )
        catalogue2 = Catalogue(
            id=2,
            name="Catalogue 2",
            is_enabled=True,
            is_active=True,
            display_order=2
        )
        
        with patch.object(db_session, 'query') as mock_query:
            # Mock the chain: query.join.filter.order_by.all
            mock_query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [
                catalogue1, catalogue2
            ]
            
            mock_check_permission.side_effect = lambda u, cid, db: cid == 1
            
            result = await get_catalogues(current_user=user, db=db_session)
            
            assert len(result) == 1
            assert result[0].id == 1
    
    @pytest.mark.asyncio
    @patch('app.api.v1.catalogues.check_catalogue_permission')
    async def test_get_catalogue_success(self, mock_check_permission, db_session):
        """Test getting a specific catalogue"""
        user = User(id=1, username="testuser", is_active=True)
        catalogue = Catalogue(
            id=1,
            name="Catalogue 1",
            is_enabled=True,
            is_active=True
        )
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = catalogue
            mock_check_permission.return_value = True
            
            result = await get_catalogue(catalogue_id=1, current_user=user, db=db_session)
            
            assert result.id == 1
            assert result.name == "Catalogue 1"
    
    @pytest.mark.asyncio
    @patch('app.api.v1.catalogues.check_catalogue_permission')
    async def test_get_catalogue_not_found(self, mock_check_permission, db_session):
        """Test getting non-existent catalogue"""
        user = User(id=1, username="testuser", is_active=True)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_catalogue(catalogue_id=999, current_user=user, db=db_session)
            
            assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    @patch('app.api.v1.catalogues.check_catalogue_permission')
    async def test_get_catalogue_access_denied(self, mock_check_permission, db_session):
        """Test getting catalogue without permission"""
        user = User(id=1, username="testuser", is_active=True)
        catalogue = Catalogue(id=1, name="Catalogue 1", is_enabled=True, is_active=True)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = catalogue
            mock_check_permission.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                await get_catalogue(catalogue_id=1, current_user=user, db=db_session)
            
            assert exc_info.value.status_code == 403
    
    @patch('app.api.v1.catalogues.is_admin_user')
    def test_check_catalogue_permission_admin(self, mock_is_admin, db_session):
        """Test catalogue permission check for admin user"""
        user = User(id=1, username="admin", is_active=True)
        mock_is_admin.return_value = True
        
        result = check_catalogue_permission(user, catalogue_id=1, db=db_session)
        
        assert result is True
        mock_is_admin.assert_called_once_with(user, db_session)
    
    @patch('app.api.v1.catalogues.is_admin_user')
    def test_check_catalogue_permission_no_access(self, mock_is_admin, db_session):
        """Test catalogue permission check for user without access"""
        user = User(id=1, username="testuser", is_active=True)
        mock_is_admin.return_value = False
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = []
            mock_query.return_value.filter.return_value.first.return_value = None
            
            result = check_catalogue_permission(user, catalogue_id=1, db=db_session)
            
            assert result is False

