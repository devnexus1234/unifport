from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import authenticate_ldap, create_access_token, create_refresh_token, verify_token, get_user_groups_ldap
from app.core.config import settings
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest
from app.models.user import User
from app.models.rbac import UserRole, Role
from typing import List

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token using the security module
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    if username is None or user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint with LDAP authentication"""
    # Authenticate with LDAP (or bypass in debug mode)
    if not authenticate_ldap(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database - user must exist
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please contact administrator to create your account.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Get user groups from LDAP
    ldap_groups = get_user_groups_ldap(login_data.username)
    
    # Get user roles from database
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_names = []
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            role_names.append(role.name)
    
    # Check if user has Admin role (in addition to is_admin flag)
    has_admin_role = "Admin" in role_names
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin or has_admin_role,  # Admin via flag or role
            "roles": role_names,
            "ldap_groups": ldap_groups
        }
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Get user roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_names = [db.query(Role).filter(Role.id == ur.role_id).first().name for ur in user_roles if db.query(Role).filter(Role.id == ur.role_id).first()]
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "roles": role_names,
            "ldap_groups": []
        }
    }

@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    from app.utils.rbac import is_admin_user
    
    # Get user roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    role_names = []
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            role_names.append(role.name)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_admin": is_admin_user(current_user, db),  # Check via flag or role
        "is_active": current_user.is_active,
        "roles": role_names
    }
