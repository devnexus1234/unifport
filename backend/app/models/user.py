from sqlalchemy import Column, Integer, String, Boolean, DateTime, Sequence
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.time_utils import get_ist_time

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, Sequence('users_seq'), primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    updated_at = Column(DateTime(timezone=True), default=get_ist_time, onupdate=get_ist_time)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

