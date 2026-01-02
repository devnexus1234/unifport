from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text, Sequence
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association table for many-to-many relationship
user_role_association = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, Sequence('roles_seq'), primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")
    permissions = relationship("Permission", back_populates="role", cascade="all, delete-orphan")
    catalogue_permissions = relationship("CatalogueRolePermission", back_populates="role", cascade="all, delete-orphan")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, Sequence('permissions_seq'), primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # 'catalogue', 'menu', 'admin'
    resource_id = Column(Integer)  # ID of the resource (catalogue_id, menu_id, etc.)
    action = Column(String(50), nullable=False)  # 'read', 'write', 'admin'
    
    # Relationships
    role = relationship("Role", back_populates="permissions")

class UserRole(Base):
    __tablename__ = "user_role_mapping"
    
    id = Column(Integer, Sequence('user_role_mapping_seq'), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_dl = Column(Boolean, default=False)  # True if this is a Distribution List
    dl_name = Column(String(255))  # Name of the DL if is_dl is True
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

class CataloguePermission(Base):
    __tablename__ = "catalogue_permissions"
    
    id = Column(Integer, Sequence('catalogue_permissions_seq'), primary_key=True, index=True)
    catalogue_id = Column(Integer, ForeignKey("catalogues.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null if DL-based
    dl_name = Column(String(255), nullable=True)  # Distribution List name
    permission_type = Column(String(50), nullable=False)  # 'read', 'write', 'admin'
    
    # Relationships
    catalogue = relationship("Catalogue", back_populates="permissions")

class CatalogueRolePermission(Base):
    """Role-based permissions for catalogues"""
    __tablename__ = "catalogue_role_permissions"
    
    id = Column(Integer, Sequence('catalogue_role_permissions_seq'), primary_key=True, index=True)
    catalogue_id = Column(Integer, ForeignKey("catalogues.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_type = Column(String(50), nullable=False)  # 'read', 'write', 'admin'
    
    # Relationships
    catalogue = relationship("Catalogue", back_populates="role_permissions")
    role = relationship("Role", back_populates="catalogue_permissions")



