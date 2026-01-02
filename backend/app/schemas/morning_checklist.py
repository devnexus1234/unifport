from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel


class MorningChecklistBase(BaseModel):
    hostname: str
    ip: Optional[str] = None
    location: Optional[str] = None
    application_name: str
    asset_owner: Optional[str] = None
    mc_check_date: date
    mc_status: Optional[str] = None
    mc_criticality: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    is_validated: Optional[bool] = False
    commands: Optional[str] = None


class ReachabilityWidget(BaseModel):
    total: int
    reachable: int
    failed: int
    unreachable: int


class SummaryGroup(BaseModel):
    application_name: str
    asset_owner: Optional[str] = None
    success_count: int
    error_count: int


class SummaryResponse(BaseModel):
    date: date
    reachability: ReachabilityWidget
    groups: List[SummaryGroup]


class HostnameDetail(MorningChecklistBase):
    mc_check_date: date
    mc_criticality: Optional[str] = None
    success: bool


class CommandDiff(BaseModel):
    command: Optional[str] = None
    current_output: Optional[str] = None
    previous_output: Optional[str] = None
    diff: List[str] = []
    is_validated: bool = False


class ValidationRequest(BaseModel):
    validate_comment: Optional[str] = None
    comment: Optional[str] = None


class BulkValidationRequest(BaseModel):
    date: date
    application_name: str
    asset_owner: Optional[str] = None
    validate_comment: Optional[str] = None
    comment: Optional[str] = None


class BulkValidateSelectedRequest(BaseModel):
    date: date
    hostnames: List[str]
    validate_comment: Optional[str] = None
    comment: Optional[str] = None


class BulkValidateGroupsRequest(BaseModel):
    date: date
    # List of objects identifying groups. Since groups are defined by (app, owner), we need that pair.
    # Alternatively, we can just pass a list of dicts.
    groups: List[SummaryGroup] 
    validate_comment: Optional[str] = None
    comment: Optional[str] = None


class ChecklistValidationRequest(BaseModel):
    date: date
    validate_comment: Optional[str] = None


class AggregatedValidatedHostname(BaseModel):
    hostname: str
    ip: Optional[str] = None
    application_name: str
    asset_owner: Optional[str] = None
    mc_criticality: Optional[str] = None
    mc_check_date: date
    validated_at: datetime
    validate_by: str  # We will return the Name here
    validate_comment: Optional[str] = None
    is_bulk: bool = False


class AggregatedValidatedResponse(BaseModel):
    items: List[AggregatedValidatedHostname]


class ValidationHistoryItem(BaseModel):
    hostname: str
    application_name: str
    asset_owner: Optional[str] = None
    mc_criticality: Optional[str] = None
    mc_check_date: date
    validated_at: datetime
    validate_by: str
    validate_comment: Optional[str] = None
    is_bulk: bool = False


class ValidationHistoryResponse(BaseModel):
    hostname: str
    history: List[ValidationHistoryItem]
