from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.catalogue import Catalogue, CatalogueCategory
from app.models.rbac import CataloguePermission, CatalogueRolePermission, UserRole, Role
from app.schemas.catalogue import CatalogueResponse, CatalogueCreate, CatalogueUpdate
from app.api.v1.auth import get_current_active_user
from app.utils.rbac import is_admin_user
import json

router = APIRouter(prefix="/catalogues", tags=["catalogues"])

def check_catalogue_permission(user: User, catalogue_id: int, db: Session, permission_type: str = "read"):
    """Check if user has permission to access a catalogue (user-based or role-based)"""
    # Admin users have all permissions (via is_admin flag or Admin role)
    if is_admin_user(user, db):
        return True
    
    # Get user's roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    if not role_ids:
        return False
    
    # Check if user has specific catalogue-level permissions (Role based)
    catalogue_permission = db.query(CatalogueRolePermission).filter(
        CatalogueRolePermission.catalogue_id == catalogue_id,
        CatalogueRolePermission.role_id.in_(role_ids)
    ).first()
    
    # If user has specific catalogue permission, use it
    if catalogue_permission:
        # Check if permission type matches
        if permission_type:
            return catalogue_permission.permission_type == permission_type or catalogue_permission.permission_type == "admin"
        return True
    
    # Check user-specific permissions
    user_permission = db.query(CataloguePermission).filter(
        CataloguePermission.catalogue_id == catalogue_id,
        CataloguePermission.user_id == user.id,
        CataloguePermission.permission_type == permission_type
    ).first()
    
    if user_permission:
        return True
    
    # Check DL-based permissions
    for user_role in user_roles:
        if user_role.is_dl and user_role.dl_name:
            dl_permission = db.query(CataloguePermission).filter(
                CataloguePermission.catalogue_id == catalogue_id,
                CataloguePermission.dl_name == user_role.dl_name,
                CataloguePermission.permission_type == permission_type
            ).first()
            if dl_permission:
                return True
    
    return False

@router.get("/", response_model=List[CatalogueResponse])
async def get_catalogues(
    category_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all enabled catalogues accessible to the user"""
    query = db.query(Catalogue).join(CatalogueCategory).filter(
        Catalogue.is_enabled == True, 
        Catalogue.is_active == True,
        CatalogueCategory.is_active == True  # Only check is_active for categories
    )
    
    if category_id:
        query = query.filter(Catalogue.category_id == category_id)
    
    catalogues = query.order_by(Catalogue.display_order).all()
    
    # Filter by RBAC
    accessible_catalogues = []
    for catalogue in catalogues:
        if check_catalogue_permission(current_user, catalogue.id, db):
            accessible_catalogues.append(catalogue)
    
    return accessible_catalogues

@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all active categories for public use (header dropdown) - only returns categories where is_active=True"""
    categories = db.query(CatalogueCategory).filter(
        CatalogueCategory.is_active == True
    ).order_by(CatalogueCategory.display_order).all()
    
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "icon": cat.icon,
            "display_order": cat.display_order
        }
        for cat in categories
    ]

@router.get("/{catalogue_id}", response_model=CatalogueResponse)
async def get_catalogue(
    catalogue_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific catalogue"""
    catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    if not catalogue:
        raise HTTPException(status_code=404, detail="Catalogue not found")
    
    if not check_catalogue_permission(current_user, catalogue_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return catalogue

