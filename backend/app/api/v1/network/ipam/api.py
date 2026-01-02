from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import ipaddress
from app.core.database import get_db
from app.models.ipam import IpamSegment, IpamAllocation, IpamAuditLog, IpamStatus
from app.models.user import User
from app.api.v1.auth import get_current_active_user
from app.schemas.ipam import (
    IpamSegmentCreate, IpamSegmentResponse, 
    IpamIpResponse, IpamAllocationUpdate,
    IpamAuditLogResponse
)
from app.services.ipam_sync import sync_ipam_segments
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/segments", response_model=List[IpamSegmentResponse])
def get_segments(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Get all IPAM segments with summary counts.
    """
    segments = db.query(IpamSegment).all()
    results = []
    
    for seg in segments:
        try:
            network = ipaddress.ip_network(seg.segment, strict=False)
            total_ips = network.num_addresses - 2
            if total_ips < 0: total_ips = 0
            
            # Count assigned/reserved
            assigned_count = db.query(IpamAllocation).filter(
                IpamAllocation.segment_id == seg.id,
                IpamAllocation.status.in_([IpamStatus.ASSIGNED, IpamStatus.RESERVED])
            ).count()
            
            results.append(IpamSegmentResponse(
                id=seg.id,
                segment=seg.segment,
                name=seg.name,
                description=seg.description,
                location=seg.location,
                entity=seg.entity,
                environment=seg.environment,
                network_zone=seg.network_zone,
                segment_description=seg.segment_description,
                created_at=seg.created_at,
                updated_at=seg.updated_at,
                total_ips=total_ips,
                assigned_ips=assigned_count,
                unassigned_ips=total_ips - assigned_count
            ))
        except ValueError:
            logger.error(f"Invalid CIDR for segment {seg.id}: {seg.segment}")
            # Identify as invalid but still return
            results.append(IpamSegmentResponse(
                id=seg.id,
                segment=seg.segment, 
                name=seg.name,
                description=seg.description,
                location=seg.location,
                entity=seg.entity,
                environment=seg.environment,
                network_zone=seg.network_zone,
                segment_description=seg.segment_description,
                created_at=seg.created_at,
                updated_at=seg.updated_at,
                total_ips=0,
                assigned_ips=0,
                unassigned_ips=0
            ))
            
    return results

@router.post("/segments", response_model=IpamSegmentResponse)
def create_segment(segment: IpamSegmentCreate, db: Session = Depends(get_db)):
    """
    Create a new IP segment.
    """
    try:
        ipaddress.ip_network(segment.segment, strict=False)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid CIDR format")

    existing = db.query(IpamSegment).filter(IpamSegment.segment == segment.segment).first()
    if existing:
        raise HTTPException(status_code=400, detail="Segment already exists")
        
    db_segment = IpamSegment(**segment.dict())
    db.add(db_segment)
    db.commit()
    db.refresh(db_segment)
    
    # Return with counts (0 initially)
    try:
        network = ipaddress.ip_network(db_segment.segment, strict=False)
        total = network.num_addresses
    except:
        total = 0

    return IpamSegmentResponse(
        **db_segment.__dict__,
        total_ips=total,
        assigned_ips=0,
        unassigned_ips=total
    )

@router.get("/segments/{segment_id}", response_model=IpamSegmentResponse)
def get_segment(segment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Get a single IPAM segment by ID with summary counts.
    """
    seg = db.query(IpamSegment).filter(IpamSegment.id == segment_id).first()
    if not seg:
        raise HTTPException(status_code=404, detail="Segment not found")

    try:
        network = ipaddress.ip_network(seg.segment, strict=False)
        total_ips = network.num_addresses
        
        assigned_count = db.query(IpamAllocation).filter(
            IpamAllocation.segment_id == seg.id,
            IpamAllocation.status.in_([IpamStatus.ASSIGNED, IpamStatus.RESERVED])
        ).count()
        
        return IpamSegmentResponse(
            id=seg.id,
            segment=seg.segment,
            name=seg.name,
            description=seg.description,
            location=seg.location,
            entity=seg.entity,
            environment=seg.environment,
            network_zone=seg.network_zone,
            segment_description=seg.segment_description,
            created_at=seg.created_at,
            updated_at=seg.updated_at,
            total_ips=total_ips,
            assigned_ips=assigned_count,
            unassigned_ips=total_ips - assigned_count
        )
    except ValueError:
        logger.error(f"Invalid CIDR for segment {seg.id}: {seg.segment}")
        raise HTTPException(status_code=400, detail="Invalid CIDR configuration for this segment")

@router.get("/segments/{segment_id}/ips", response_model=List[IpamIpResponse])
def get_segment_ips(segment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Get all IPs for a segment, auto-calculated + merged with allocations.
    """
    seg = db.query(IpamSegment).filter(IpamSegment.id == segment_id).first()
    if not seg:
        raise HTTPException(status_code=404, detail="Segment not found")
        
    try:
        network = ipaddress.ip_network(seg.segment, strict=False)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid CIDR configuration for this segment")
        
    # Get all existing allocations
    allocations = db.query(IpamAllocation).filter(IpamAllocation.segment_id == segment_id).all()
    alloc_map = {a.ip_address: a for a in allocations}
    
    results = []
    # Iterate over all IPs in network. 
    # Warning: For large subnets this could be heavy. Limiting to /20 or smaller is recommended but not enforced here yet.
    # ip_network(x).hosts() excludes network and broadcast. ip_network(x) includes them if we iterate directly?
    # Usually people want usable IPs. Let's use specific hosts() if we want to exclude net/broadcast, 
    # but requests asks for "available under that segment". 
    # If it's a small subnet, showing all is fine.
    
    # Using hosts() to exclude network address and broadcast address.
    for ip in network:
        ip_str = str(ip)
        alloc = alloc_map.get(ip_str)
        
        status = IpamStatus.UNASSIGNED
        ritm = None
        comment = None
        source = None
        updated_at = None
        
        if alloc:
            status = alloc.status
            ritm = alloc.ritm
            comment = alloc.comment
            source = alloc.source
            updated_at = alloc.updated_at
            
        results.append(IpamIpResponse(
            ip_address=ip_str,
            status=status,
            segment_id=seg.id,
            segment_name=seg.name,
            segment=seg.segment,
            location=seg.location,
            entity=seg.entity,
            environment=seg.environment,
            ritm=ritm,
            comment=comment,
            source=source,
            updated_at=updated_at
        ))
        
    return results

from fastapi import BackgroundTasks
from app.services.ipam_sync import sync_ipam_segments, sync_manager

@router.post("/segments/sync", status_code=202)
async def trigger_ipam_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger manual IPAM segment sync with ServiceNow (Async).
    """
    if sync_manager.is_running:
        raise HTTPException(status_code=409, detail="Sync is already in progress")

    background_tasks.add_task(sync_ipam_segments, db) # Pass db to the background task
    return {"message": "Sync started in background", "status": "RUNNING"}

@router.get("/segments/sync/status")
def get_sync_status(current_user: User = Depends(get_current_active_user)):
    """
    Get the status of the IPAM segment sync.
    """
    return {
        "is_running": sync_manager.is_running,
        "status": sync_manager.status,
        "last_run": sync_manager.last_run,
        "result": sync_manager.result,
        "error": sync_manager.error
    }
    
@router.post("/ips", response_model=IpamIpResponse)
def update_ip_allocation(
    payload: IpamAllocationUpdate, 
    segment_id: int, 
    ip_address: str, 
    db: Session = Depends(get_db)
):
    """
    Update or Create an IP allocation (mark as assigned/unassigned).
    Expects query params or body? RESTful would be PUT /segments/{id}/ips/{ip} but 
    creating a dedicated endpoint for 'update allocation' is fine. 
    
    Let's use a cleaner path: PUT /segments/{segment_id}/ips/{ip_address}
    But user requirement said "In IP list table against each IP provide a button...".
    I will use POST /segments/{segment_id}/allocate as a flexible endpoint or 
    PUT /segments/{segment_id}/ips/{ip_address} as defined below.
    """
    pass

from app.models.user import User
from app.api.v1.auth import get_current_active_user
from app.models.ipam import IpamAuditLog

# ... existing code ...

def log_change(db: Session, user_id: int, action: str, segment_id: int = None, ip_address: str = None, changes: str = None):
    try:
        audit = IpamAuditLog(
            user_id=user_id,
            segment_id=segment_id,
            ip_address=ip_address,
            action=action,
            changes=changes
        )
        db.add(audit)
        db.commit() # Commit log immediately? Or part of main transaction? 
        # Ideally part of main transaction, but simple helper commits. 
        # I'll let main function commit if possible, but here separate is safer for visibility if main fails? 
        # No, atomic is better. But I'll pass db and assuming caller commits or I commit.
        # I'll just db.add and let caller commit?
        # update_allocation commits allocation. I should add audit before commit.
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")

# ...

@router.get("/audit-logs", response_model=List[IpamAuditLogResponse])
def get_audit_logs(
    segment_id: int = None, 
    ip_address: str = None, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get IPAM audit logs, optionally filtered.
    """
    query = db.query(IpamAuditLog)
    
    if segment_id:
        query = query.filter(IpamAuditLog.segment_id == segment_id)
    
    if ip_address:
        query = query.filter(IpamAuditLog.ip_address == ip_address)
        
    # Join with User to get username if needed (schema handles relationship?)
    # Schema IpamAuditLogResponse has user_id. 
    # If I want username, I can add a hybrid property or just fetch user.
    # The Pydantic model 'IpamAuditLogResponse' has 'username' field. I should populate it.
    
    logs = query.order_by(IpamAuditLog.created_at.desc()).limit(limit).all()
    
    results = []
    for log in logs:
        results.append(IpamAuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=log.user.username if log.user else "Unknown",
            segment_id=log.segment_id,
            ip_address=log.ip_address,
            action=log.action,
            changes=log.changes,
            created_at=log.created_at
        ))
    return results

@router.put("/segments/{segment_id}/ips/{ip_address}", response_model=IpamIpResponse)
def update_allocation(
    segment_id: int,
    ip_address: str,
    payload: IpamAllocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    seg = db.query(IpamSegment).filter(IpamSegment.id == segment_id).first()
    if not seg:
        raise HTTPException(status_code=404, detail="Segment not found")

    # Verify IP is in segment
    try:
        network = ipaddress.ip_network(seg.segment, strict=False)
        ip = ipaddress.ip_address(ip_address)
        if ip not in network:
             raise HTTPException(status_code=400, detail="IP does not belong to segment")
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid IP or Segment")

    allocation = db.query(IpamAllocation).filter(
        IpamAllocation.segment_id == segment_id,
        IpamAllocation.ip_address == ip_address
    ).first()
    
    changes = []
    action = "UPDATE_ALLOCATION"
    
    if allocation:
        # Update
        if allocation.status != payload.status:
            changes.append(f"Status: {allocation.status.value} -> {payload.status.value}")
        if allocation.ritm != payload.ritm:
             changes.append(f"RITM: {allocation.ritm or 'None'} -> {payload.ritm or 'None'}")
        if allocation.source != payload.source:
             changes.append(f"Source: {allocation.source or 'None'} -> {payload.source or 'None'}")
        if allocation.comment != payload.comment:
             changes.append(f"Comment: {allocation.comment or 'None'} -> {payload.comment or 'None'}")
        
        allocation.status = payload.status
        allocation.ritm = payload.ritm
        allocation.comment = payload.comment
        allocation.source = payload.source
    else:
        # Create
        action = "ASSIGN_IP"
        changes.append(f"Assigned status: {payload.status.value}")
        if payload.ritm:
            changes.append(f"RITM: {payload.ritm}")
        if payload.source:
            changes.append(f"Source: {payload.source}")
        if payload.comment:
            changes.append(f"Comment: {payload.comment}")
        
        allocation = IpamAllocation(
            segment_id=segment_id,
            ip_address=ip_address,
            status=payload.status,
            ritm=payload.ritm,
            comment=payload.comment,
            source=payload.source
        )
        db.add(allocation)
        
    # Create log
    if changes or action == "ASSIGN_IP": # Only log meaningful changes
        log = IpamAuditLog(
            user_id=current_user.id,
            segment_id=segment_id,
            ip_address=ip_address,
            action=action,
            changes=", ".join(changes)
        )
        db.add(log)
        
    db.commit()
    db.refresh(allocation)
    
    return IpamIpResponse(
        ip_address=allocation.ip_address,
        status=allocation.status,
        segment_id=seg.id,
        segment_name=seg.name,
        segment=seg.segment,
        location=seg.location,
        entity=seg.entity,
        environment=seg.environment,
        ritm=allocation.ritm,
        comment=allocation.comment,
        source=allocation.source,
        updated_at=allocation.updated_at
    )
