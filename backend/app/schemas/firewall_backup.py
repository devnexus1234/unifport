from typing import Optional
from datetime import date
from pydantic import BaseModel

class FirewallBackupBase(BaseModel):
    task_date: date
    task_name: str
    host_count: int = 0
    failed_count: int = 0
    failed_hosts: Optional[str] = None
    successful_hosts: Optional[str] = None

class FirewallBackupCreate(FirewallBackupBase):
    pass

class FirewallBackup(FirewallBackupBase):
    id: int

    class Config:
        from_attributes = True

class BackupSummary(BaseModel):
    total_devices: int
    success_count: int
    failed_count: int
