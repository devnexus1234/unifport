from typing import List, Any, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.firewall_backup import FirewallBackup
from app.schemas.firewall_backup import FirewallBackup as FirewallBackupSchema, BackupSummary

router = APIRouter()

@router.get("/reports", response_model=List[FirewallBackupSchema])
def read_firewall_backups(
    skip: int = 0,
    limit: int = 100,
    task_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve firewall backup reports.
    """
    query = db.query(FirewallBackup)
    
    if task_date:
        query = query.filter(FirewallBackup.task_date == task_date)
        
    backups = query.order_by(FirewallBackup.task_date.desc()).offset(skip).limit(limit).all()
    return backups

@router.get("/summary", response_model=BackupSummary)
def get_backup_summary(db: Session = Depends(get_db)):
    """
    Get aggregated summary of firewall backups.
    """
    # Calculate totals directly from the database
    # Total Devices = Sum of host_count
    # Failed = Sum of failed_count
    # Success = Total Devices - Failed (or sum of successful_hosts count if parsed, but mathematically Total - Failed should match provided schema logic)
    
    from datetime import date
    today = date.today()
    
    # Using coalesce to handle potential None values as 0
    stats = db.query(
        func.sum(FirewallBackup.host_count).label("total"),
        func.sum(FirewallBackup.failed_count).label("failed")
    ).filter(FirewallBackup.task_date == today).first()
    
    total_devices = stats.total if stats.total else 0
    failed_count = stats.failed if stats.failed else 0
    success_count = total_devices - failed_count
    
    return {
        "total_devices": total_devices,
        "failed_count": failed_count,
        "success_count": success_count
    }
