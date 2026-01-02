"""
Enhanced fixtures for authenticated API testing
"""
import pytest
from typing import Dict, Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.rbac import Role, UserRole
from app.core.security import create_access_token, get_password_hash

@pytest.fixture(scope="function")
def admin_user(test_db: Session) -> User:
    """Create an admin user for testing"""
    user = test_db.query(User).filter(User.username == "admin").first()
    if not user:
        user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            is_active=True,
            is_admin=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def regular_user(test_db: Session) -> User:
    """Create a regular user for testing"""
    user = test_db.query(User).filter(User.username == "regular").first()
    if not user:
        user = User(
            username="regular",
            email="regular@example.com",
            full_name="Regular User",
            is_active=True,
            is_admin=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def inactive_user(test_db: Session) -> User:
    """Create an inactive user for testing"""
    user = test_db.query(User).filter(User.username == "inactive").first()
    if not user:
        user = User(
            username="inactive",
            email="inactive@example.com",
            full_name="Inactive User",
            is_active=False,
            is_admin=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_token_headers(admin_user: User) -> Dict[str, str]:
    """Get auth headers for admin user"""
    access_token = create_access_token(
        data={"sub": admin_user.username, "user_id": admin_user.id, "email": admin_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def regular_token_headers(regular_user: User) -> Dict[str, str]:
    """Get auth headers for regular user"""
    access_token = create_access_token(
        data={"sub": regular_user.username, "user_id": regular_user.id, "email": regular_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def user_with_role(test_db: Session) -> User:
    """Create a user with a specific role"""
    # Create role if it doesn't exist
    role = test_db.query(Role).filter(Role.name == "TestRole").first()
    if not role:
        role = Role(name="TestRole", description="Test role")
        test_db.add(role)
        test_db.commit()
        test_db.refresh(role)
    
    # Create user
    user = test_db.query(User).filter(User.username == "roleuser").first()
    if not user:
        user = User(
            username="roleuser",
            email="roleuser@example.com",
            full_name="Role User",
            is_active=True,
            is_admin=False
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Assign role
        user_role = UserRole(user_id=user.id, role_id=role.id)
        test_db.add(user_role)
        test_db.commit()
    
    return user
