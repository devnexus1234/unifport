from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class IpamStatus(str, Enum):
    ASSIGNED = "Assigned"
    UNASSIGNED = "Unassigned"
    RESERVED = "Reserved"

# --- Segment Schemas ---

class IpamSegmentBase(BaseModel):
    segment: str
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    entity: Optional[str] = None
    environment: Optional[str] = None
    network_zone: Optional[str] = None
    segment_description: Optional[str] = None

class IpamSegmentCreate(IpamSegmentBase):
    pass

class IpamSegmentUpdate(IpamSegmentBase):
    segment: Optional[str] = None

class IpamSegmentResponse(IpamSegmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Counts
    total_ips: int = 0
    assigned_ips: int = 0
    unassigned_ips: int = 0

    model_config = ConfigDict(from_attributes=True)

# --- Allocation/IP Schemas ---

class IpamAllocationBase(BaseModel):
    ritm: Optional[str] = Field(None, pattern=r"^RITM\d{7}$")
    comment: Optional[str] = None
    source: Optional[str] = None
    status: IpamStatus = IpamStatus.UNASSIGNED

class IpamAllocationUpdate(IpamAllocationBase):
    pass

class IpamIpResponse(BaseModel):
    ip_address: str
    status: IpamStatus
    segment_id: int
    # Merged segment info usually valid for these
    segment_name: Optional[str] = None
    segment: Optional[str] = None
    location: Optional[str] = None
    entity: Optional[str] = None
    environment: Optional[str] = None
    
    # Allocation specific
    ritm: Optional[str] = None
    comment: Optional[str] = None
    source: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Audit Log Schemas ---

class IpamAuditLogResponse(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None # Helper to show username directly
    segment_id: Optional[int] = None
    ip_address: Optional[str] = None
    action: str
    changes: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
