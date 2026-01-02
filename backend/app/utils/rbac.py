"""
RBAC utility functions for checking user permissions
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.rbac import UserRole, Role


def is_admin_user(user: User, db: Session) -> bool:
    """
    Check if a user has admin privileges.
    
    A user is considered admin if:
    1. They have the is_admin flag set to True, OR
    2. They have the "Admin" role assigned
    
    Args:
        user: The user to check
        db: Database session
        
    Returns:
        True if user is admin, False otherwise
    """
    # Check is_admin flag
    if user.is_admin:
        return True
    
    # Check if user has "Admin" role
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    if not user_roles:
        return False
    
    role_ids = [ur.role_id for ur in user_roles]
    admin_role = db.query(Role).filter(
        Role.id.in_(role_ids),
        Role.name == "Admin"
    ).first()
    
    return admin_role is not None
