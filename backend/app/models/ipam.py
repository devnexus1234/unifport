from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum, Sequence
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.time_utils import get_ist_time

class IpamStatus(str, enum.Enum):
    ASSIGNED = "Assigned"
    UNASSIGNED = "Unassigned"
    RESERVED = "Reserved"

class IpamSegment(Base):
    __tablename__ = "ipam_segments"
    
    id = Column(Integer, Sequence('ipam_segments_seq'), primary_key=True)
    segment = Column(String(50), unique=True, nullable=False)  # CIDR e.g., 171.11.11.11/24
    name = Column(String(100))
    description = Column(Text)
    location = Column(String(100))
    entity = Column(String(100))
    environment = Column(String(100))
    network_zone = Column(String(100))
    segment_description = Column(Text) # Explicitly requested "segment description" separate from description? Using this for now.
    
    # We can probably calculate total_ips on the fly, but storing might be useful for sorting/filtering if needed.
    # For now, let's keep it simple and calculate it.
    
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    updated_at = Column(DateTime(timezone=True), default=get_ist_time, onupdate=get_ist_time)

    # Relationships
    allocations = relationship("IpamAllocation", back_populates="segment", cascade="all, delete-orphan")

class IpamAllocation(Base):
    __tablename__ = "ipam_allocations"
    
    id = Column(Integer, Sequence('ipam_allocations_seq'), primary_key=True)
    segment_id = Column(Integer, ForeignKey("ipam_segments.id"), nullable=False)
    ip_address = Column(String(50), nullable=False) # The specific IP, e.g., 171.11.11.12
    status = Column(SQLEnum(IpamStatus), default=IpamStatus.UNASSIGNED)
    ritm = Column(String(100))
    comment = Column(Text)
    source = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    updated_at = Column(DateTime(timezone=True), default=get_ist_time, onupdate=get_ist_time)
    
    # Relationships
    segment = relationship("IpamSegment", back_populates="allocations")

class IpamAuditLog(Base):
    __tablename__ = "ipam_audit_logs"
    
    id = Column(Integer, Sequence('ipam_audit_logs_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("ipam_segments.id"), nullable=True) # Nullable if global or deleted? Let's say nullable.
    ip_address = Column(String(50), nullable=True) 
    action = Column(String(50), nullable=False)
    changes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    
    # Relationships
    user = relationship("User")
    segment = relationship("IpamSegment")
