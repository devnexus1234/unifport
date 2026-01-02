from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum, Sequence
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.time_utils import get_ist_time

class CatalogueCategoryEnum(str, enum.Enum):
    STORAGE = "Storage"
    FIREWALL = "Firewall"
    BACKUP = "Backup"
    NETWORK = "Network"
    SECURITY = "Security"
    MONITORING = "Monitoring"
    OTHER = "Other"

class CatalogueCategory(Base):
    __tablename__ = "catalogue_categories"
    
    id = Column(Integer, Sequence('catalogue_categories_seq'), primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(100))  # Icon class or path
    display_order = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    
    # Relationships
    catalogues = relationship("Catalogue", back_populates="category", cascade="all, delete-orphan")

class Catalogue(Base):
    __tablename__ = "catalogues"
    
    id = Column(Integer, Sequence('catalogues_seq'), primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("catalogue_categories.id"), nullable=False)  # Category is main grouping now
    api_endpoint = Column(String(500))  # API endpoint for the catalogue
    frontend_route = Column(String(255))  # Frontend route path
    icon = Column(String(100))
    is_enabled = Column(Boolean, default=False)  # Only enabled catalogues are visible
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    config = Column(Text)  # JSON configuration for the catalogue
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    updated_at = Column(DateTime(timezone=True), default=get_ist_time, onupdate=get_ist_time)
    
    # Relationships
    category = relationship("CatalogueCategory", back_populates="catalogues")
    permissions = relationship("CataloguePermission", back_populates="catalogue", cascade="all, delete-orphan")
    role_permissions = relationship("CatalogueRolePermission", back_populates="catalogue", cascade="all, delete-orphan")

