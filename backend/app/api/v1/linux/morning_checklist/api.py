from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Dict, List, Tuple, Optional

import difflib
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.models.user import User
from app.core.time_utils import get_ist_time
from app.models.morning_checklist import MorningChecklist, MorningChecklistValidation, MorningChecklistSignOff
from app.schemas.morning_checklist import (
    SummaryResponse,
    SummaryGroup,
    ReachabilityWidget,
    HostnameDetail,
    CommandDiff,
    ValidationRequest,
    BulkValidationRequest,
    BulkValidateSelectedRequest,
    BulkValidateGroupsRequest,
    AggregatedValidatedHostname,
    AggregatedValidatedResponse,
    ValidationHistoryResponse,
    ValidationHistoryItem,
    ChecklistValidationRequest,
)
# Lazy import to avoid circular dependency if any, but standard import should work
# from .services.report_generator import generate_morning_checklist_excel (Imported inside function)

router = APIRouter(prefix="/linux/morning-checklist", tags=["linux/morning-checklist"])


def _get_prev_date(target_date: date) -> date:
    return target_date - timedelta(days=1)


def _load_rows(
    db: Session,
    target_date: date,
    application_name: Optional[str],
    asset_owner: Optional[str],
) -> List[MorningChecklist]:
    query = db.query(MorningChecklist).filter(MorningChecklist.mc_check_date == target_date)
    if application_name:
        query = query.filter(MorningChecklist.application_name == application_name)
    if asset_owner:
        query = query.filter(MorningChecklist.asset_owner == asset_owner)
    return query.all()


def _build_host_maps(rows: List[MorningChecklist]) -> Dict[str, List[MorningChecklist]]:
    hosts: Dict[str, List[MorningChecklist]] = {}
    for row in rows:
        hosts.setdefault(row.hostname, []).append(row)
    return hosts


def _compare_host(
    host_rows: List[MorningChecklist],
    prev_rows: List[MorningChecklist],
    return_all: bool = False,
) -> Tuple[bool, List[CommandDiff]]:
    """Returns (is_success, diffs)."""
    validated = any(r.is_validated for r in host_rows)

    # If prev_rows is empty, it means no data for previous date.
    # User requested to treat this as Success and show "No data found".
    if not prev_rows:
        diffs = []
        # If we need to return details (return_all=True), we must generate them.
        # But wait, if return_all is False, we just return True, [] (Success).
        if not return_all:
             return True, []
        
        # If return_all is True, we generate entries for all current commands
        current_map: Dict[str, Optional[str]] = {r.commands or "": r.mc_output for r in host_rows}
        for cmd in sorted(current_map.keys()):
            cur = current_map.get(cmd, "")
            # We use a placeholder for previous output, but diff=[] to indicate NO highlighting/Side-by-side normal view
            diffs.append(
                CommandDiff(
                    command=cmd,
                    current_output=cur,
                    previous_output="No data found for previous date",
                    diff=[], 
                    is_validated=validated,
                )
            )
        return True, diffs

    # Build command -> output maps
    current_map: Dict[str, Optional[str]] = {r.commands or "": r.mc_output for r in host_rows}
    prev_map: Dict[str, Optional[str]] = {r.commands or "": r.mc_output for r in prev_rows}

    all_commands = set(current_map.keys()) | set(prev_map.keys())
    diffs: List[CommandDiff] = []
    has_diff = False

    for cmd in sorted(all_commands):
        cur = current_map.get(cmd, "")
        prev = prev_map.get(cmd, "")
        if (cur or "") != (prev or ""):
            has_diff = True
            diff_lines = list(
                difflib.unified_diff(
                    (prev or "").splitlines(),
                    (cur or "").splitlines(),
                    fromfile="D-1",
                    tofile="D",
                    lineterm="",
                )
            )
            diffs.append(
                CommandDiff(
                    command=cmd,
                    current_output=cur,
                    previous_output=prev,
                    diff=diff_lines,
                    is_validated=validated,
                )
            )
        elif return_all:
            diffs.append(
                CommandDiff(
                    command=cmd,
                    current_output=cur,
                    previous_output=prev,
                    diff=[],
                    is_validated=validated,
                )
            )

    is_success = not has_diff
    if validated:
        is_success = True

    return (is_success, diffs)


@router.get("/filters/application-owners")
async def get_application_owner_mapping(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get mapping of application names to their asset owners"""
    try:
        rows = (
            db.query(MorningChecklist.application_name, MorningChecklist.asset_owner)
            .distinct()
            .order_by(MorningChecklist.application_name)
            .all()
        )
        mapping: Dict[str, List[str]] = {}
        for app, owner in rows:
            if not app:
                continue
            if app not in mapping:
                mapping[app] = []
            if owner and owner not in mapping[app]:
                mapping[app].append(owner)
        # Sort owners within each application
        for app in mapping:
            mapping[app].sort()
        return mapping
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching application-owner mapping: {str(e)}")


@router.get("/dates")
async def get_last_7_dates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the last 7 dates with data from the morning checklist"""
    logger = get_logger(__name__)
    
    if db is None:
        logger.error("Database session is None")
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Use a fresh query to avoid any session state issues
        query = db.query(MorningChecklist.mc_check_date)
        dates = (
            query.distinct()
            .order_by(desc(MorningChecklist.mc_check_date))
            .limit(7)
            .all()
        )
        # Convert date objects to ISO format strings (YYYY-MM-DD)
        result = []
        for d in dates:
            if d and d[0]:
                try:
                    result.append(d[0].isoformat())
                except (AttributeError, TypeError) as e:
                    logger.warning(f"Error converting date {d}: {e}")
                    continue
        return result
    except Exception as e:
        logger.error(f"Error fetching dates: {e}", exc_info=True)
        # Ensure we don't leave the session in a bad state
        try:
            if db:
                db.rollback()
        except Exception as rollback_error:
            logger.warning(f"Error during rollback: {rollback_error}")
        raise HTTPException(status_code=500, detail=f"Error fetching dates: {str(e)}")


@router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    date_param: date = Query(..., alias="date"),
    application_name: Optional[str] = None,
    asset_owner: Optional[str] = None,
    show_errors_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    current_rows = _load_rows(db, date_param, application_name, asset_owner)
    previous_rows = _load_rows(db, _get_prev_date(date_param), application_name, asset_owner)

    current_hosts = _build_host_maps(current_rows)
    previous_hosts = _build_host_maps(previous_rows)

    # Reachability widget - Count UNIQUE hostnames
    # We assume mc_status is consistent across rows for the same hostname (e.g. host is reachable or not)
    # If it varies, we might need aggregation logic, but taking the first row is standard for host-level status.
    
    total_hosts = len(current_hosts)
    reachable_hosts = 0
    failed_hosts = 0
    unreachable_hosts = 0
    
    for _, rows in current_hosts.items():
        if not rows: continue
        status = (rows[0].mc_status or "").lower()
        if status == "reachable":
            reachable_hosts += 1
        elif status == "failed":
            failed_hosts += 1
        elif status == "unreachable":
             unreachable_hosts += 1

    reachability = ReachabilityWidget(
        total=total_hosts,
        reachable=reachable_hosts,
        failed=failed_hosts,
        unreachable=unreachable_hosts,
    )

    groups: Dict[Tuple[str, Optional[str]], SummaryGroup] = {}

    for hostname, rows in current_hosts.items():
        prev = previous_hosts.get(hostname, [])
        is_success, _ = _compare_host(rows, prev)
        key = (rows[0].application_name, rows[0].asset_owner)
        if key not in groups:
            groups[key] = SummaryGroup(
                application_name=rows[0].application_name,
                asset_owner=rows[0].asset_owner,
                success_count=0,
                error_count=0,
            )
        if is_success:
            groups[key].success_count += 1
        else:
            groups[key].error_count += 1

    filtered_groups = list(groups.values())
    if show_errors_only:
        filtered_groups = [g for g in filtered_groups if g.error_count > 0]

    return SummaryResponse(date=date_param, reachability=reachability, groups=filtered_groups)


@router.get("/details", response_model=List[HostnameDetail])
async def get_hostname_details(
    date_param: date = Query(..., alias="date"),
    status: Optional[str] = Query(None, pattern="^(success|error)$"),
    mc_status: Optional[str] = None,
    application_name: Optional[str] = None,
    asset_owner: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    current_rows = _load_rows(db, date_param, application_name, asset_owner)
    previous_rows = _load_rows(db, _get_prev_date(date_param), application_name, asset_owner)

    current_hosts = _build_host_maps(current_rows)
    previous_hosts = _build_host_maps(previous_rows)

    details: List[HostnameDetail] = []
    
    # Iterate over unique hostnames
    for hostname, rows in current_hosts.items():
        if not rows: continue
        
        # Apply filtering based on status params
        
        # 1. Reachability Status Filter (mc_status) - Applies to the HOST
        if mc_status:
             target = mc_status.lower()
             if target != "total":
                  host_status = (rows[0].mc_status or "").lower()
                  if host_status != target:
                      continue
        
        prev = previous_hosts.get(hostname, [])
        is_success, _ = _compare_host(rows, prev)

        # 2. Diff Status Filter (success/error)
        if status == "success" and not is_success:
            continue
        if status == "error" and is_success:
            continue

        base = rows[0]
        details.append(
            HostnameDetail(
                hostname=hostname,
                ip=base.ip,
                location=base.location,
                application_name=base.application_name,
                asset_owner=base.asset_owner,
                mc_check_date=base.mc_check_date,
                mc_status=base.mc_status,
                mc_criticality=base.mc_criticality,
                updated_by=base.updated_by,
                updated_at=base.updated_at,
                is_validated=base.is_validated,
                commands=base.commands, # This will be from the first row. 
                # If granular command display is needed, frontend should use "View Commands"
                success=is_success,
            )
        )
            
    return details


@router.get("/hostnames/{hostname}/commands", response_model=List[CommandDiff])
async def get_command_outputs(
    hostname: str,
    date_param: date = Query(..., alias="date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = _load_rows(db, date_param, None, None)
    host_rows = [r for r in rows if r.hostname == hostname]
    if not host_rows:
        raise HTTPException(status_code=404, detail="Hostname not found for given date")
    return [
        CommandDiff(command=r.commands, current_output=r.mc_output, previous_output=None, diff=[])
        for r in host_rows
    ]


@router.get("/hostnames/{hostname}/diff", response_model=List[CommandDiff])
async def get_diff(
    hostname: str,
    date_param: date = Query(..., alias="date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    current_rows = [r for r in _load_rows(db, date_param, None, None) if r.hostname == hostname]
    prev_rows = [r for r in _load_rows(db, _get_prev_date(date_param), None, None) if r.hostname == hostname]

    if not current_rows:
        raise HTTPException(status_code=404, detail="Hostname not found for given date")

    _, diffs = _compare_host(current_rows, prev_rows, return_all=True)
    return diffs


@router.post("/hostnames/{hostname}/validate")
async def validate_hostname(
    hostname: str,
    payload: ValidationRequest,
    date_param: date = Query(..., alias="date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = db.query(MorningChecklist).filter(
        MorningChecklist.hostname == hostname,
        MorningChecklist.mc_check_date == date_param,
    )

    if not rows.first():
        raise HTTPException(status_code=404, detail="Hostname not found for given date")

    rows.update(
        {
            MorningChecklist.is_validated: True,
            MorningChecklist.updated_by: current_user.username,
            MorningChecklist.updated_at: get_ist_time(),
        }
    )

    # Store validation history
    base = rows.first()
    db.add(
        MorningChecklistValidation(
            hostname=hostname,
            application_name=base.application_name,
            asset_owner=base.asset_owner,
            mc_check_date=date_param,
            validated_at=get_ist_time(),
            validate_by=current_user.id,
            validate_comment=payload.validate_comment or payload.comment,
            mc_criticality=base.mc_criticality,
            is_bulk=False,
        )
    )
    db.commit()
    return {"status": "validated"}


@router.delete("/hostnames/{hostname}/validate")
async def undo_validation(
    hostname: str,
    date_param: date = Query(..., alias="date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # 1. Find and delete validation record
    validation = db.query(MorningChecklistValidation).filter(
        MorningChecklistValidation.hostname == hostname,
        MorningChecklistValidation.mc_check_date == date_param,
    ).first()

    if not validation:
        raise HTTPException(status_code=404, detail="Validation record not found")

    db.delete(validation)

    # 2. Reset the main checklist record
    row = db.query(MorningChecklist).filter(
        MorningChecklist.hostname == hostname,
        MorningChecklist.mc_check_date == date_param,
    ).first()

    if row:
        row.is_validated = False
        # Optionally track who undid it or just leave it as last updated by whomever
        row.updated_by = current_user.username
        row.updated_at = get_ist_time()
    
    db.commit()
    return {"status": "validation_undone"}


@router.post("/validate-all")
async def validate_all(
    payload: BulkValidationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = db.query(MorningChecklist).filter(
        MorningChecklist.mc_check_date == payload.date,
        MorningChecklist.application_name == payload.application_name,
    )
    if payload.asset_owner:
        rows = rows.filter(MorningChecklist.asset_owner == payload.asset_owner)
    
    # Only validate items that have errors (either status is not reachable OR diff status is not NO_DIFF)
    rows = rows.filter(
        or_(
            MorningChecklist.mc_status != "reachable",
            MorningChecklist.mc_diff_status != "NO_DIFF"
        )
    )

    targets = rows.all()
    if not targets:
        raise HTTPException(status_code=404, detail="No records found for filter")

    rows.update(
        {
            MorningChecklist.is_validated: True,
            MorningChecklist.updated_by: current_user.username,
            MorningChecklist.updated_at: get_ist_time(),
        },
        synchronize_session=False,
    )

    for row in targets:
        db.add(
            MorningChecklistValidation(
                hostname=row.hostname,
                application_name=row.application_name,
                asset_owner=row.asset_owner,
                mc_check_date=row.mc_check_date,
                validated_at=get_ist_time(),
                validate_by=current_user.id,
                validate_comment=payload.validate_comment or payload.comment,
                mc_criticality=row.mc_criticality,
                is_bulk=True,
            )
        )

    db.commit()
    return {"status": "validated_all", "count": len(targets)}


@router.post("/validate-selected")
async def validate_selected_hostnames(
    payload: BulkValidateSelectedRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not payload.hostnames:
        raise HTTPException(status_code=400, detail="No hostnames provided")

    rows = db.query(MorningChecklist).filter(
        MorningChecklist.mc_check_date == payload.date,
        MorningChecklist.hostname.in_(payload.hostnames)
    )

    targets = rows.all()
    if not targets:
        raise HTTPException(status_code=404, detail="No records found for provided hostnames and date")

    # Update metadata
    rows.update(
        {
            MorningChecklist.is_validated: True,
            MorningChecklist.updated_by: current_user.username,
            MorningChecklist.updated_at: get_ist_time(),
        },
        synchronize_session=False,
    )

    # Add validation entries
    for row in targets:
        db.add(
            MorningChecklistValidation(
                hostname=row.hostname,
                application_name=row.application_name,
                asset_owner=row.asset_owner,
                mc_check_date=row.mc_check_date,
                validated_at=get_ist_time(),
                validate_by=current_user.id,
                validate_comment=payload.validate_comment or payload.comment,
                mc_criticality=row.mc_criticality,
                is_bulk=True,
            )
        )

    db.commit()
    return {"status": "validated_selected", "count": len(targets)}


@router.post("/validate-groups")
async def validate_groups(
    payload: BulkValidateGroupsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not payload.groups:
        raise HTTPException(status_code=400, detail="No groups provided")

    total_count = 0
    
    # We could do one big query or one per group. Since number of groups is likely small, loop is okay.
    # Or build a complex OR condition.
    
    # Using a loop for simplicity and clarity first.
    timestamp = get_ist_time()
    
    for group in payload.groups:
        # Resolve rows for this group
        query = db.query(MorningChecklist).filter(
            MorningChecklist.mc_check_date == payload.date,
            MorningChecklist.application_name == group.application_name
        )
        if group.asset_owner:
            query = query.filter(MorningChecklist.asset_owner == group.asset_owner)
        else:
            # If asset_owner is explicitly None/Empty in group, handle that?
            # In our model, asset_owner can be null.
            # However, SummaryGroup often has 'OR None'. 
            pass

        # Also, we should probably ONLY validate ERRORS not everything?
        # Similar to validate_all logic:
        query = query.filter(
            or_(
                MorningChecklist.mc_status != "reachable",
                MorningChecklist.mc_diff_status != "NO_DIFF"
            )
        )
        
        rows = query.all()
        if not rows:
            continue
            
        count = len(rows)
        total_count += count
        
        # Batch update
        query.update(
            {
                MorningChecklist.is_validated: True,
                MorningChecklist.updated_by: current_user.username,
                MorningChecklist.updated_at: timestamp,
            },
            synchronize_session=False,
        )

        for row in rows:
            db.add(
                MorningChecklistValidation(
                    hostname=row.hostname,
                    application_name=row.application_name,
                    asset_owner=row.asset_owner,
                    mc_check_date=row.mc_check_date,
                    validated_at=timestamp,
                    validate_by=current_user.id,
                    validate_comment=payload.validate_comment or payload.comment,
                    mc_criticality=row.mc_criticality,
                    is_bulk=True,
                )
            )

    db.commit()
    return {"status": "validated_groups", "count": total_count}





@router.post("/validate-checklist")
async def validate_checklist(
    payload: ChecklistValidationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Check if already validated in SignOff table
    existing = (
        db.query(MorningChecklistSignOff)
        .filter(MorningChecklistSignOff.mc_check_date == payload.date)
        .first()
    )

    if existing:
        # Update existing
        existing.validated_at = get_ist_time()
        existing.validate_by = current_user.id
        existing.validate_comment = payload.validate_comment
    else:
        # Create new
        db.add(
            MorningChecklistSignOff(
                mc_check_date=payload.date,
                validated_at=get_ist_time(),
                validate_by=current_user.id,
                validate_comment=payload.validate_comment,
            )
        )

    db.commit()
    return {"status": "checklist_validated"}


@router.delete("/validate-checklist")
async def undo_checklist_validation(
    date_param: date = Query(..., alias="date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(MorningChecklistSignOff)
        .filter(MorningChecklistSignOff.mc_check_date == date_param)
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Checklist validation not found for this date")

    db.delete(existing)
    db.commit()
    return {"status": "checklist_validation_undone"}


@router.get("/checklist-validation-status")
async def get_checklist_validation_status(
    date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(MorningChecklistSignOff, User.full_name, User.username)
        .join(User, MorningChecklistSignOff.validate_by == User.id)
        .filter(MorningChecklistSignOff.mc_check_date == date)
        .first()
    )
    if not record:
        return None
    
    signoff, full_name, username = record
    validator_name = full_name if full_name else username

    return {
        "validate_by": validator_name,
        "validated_at": signoff.validated_at,
        "validate_comment": signoff.validate_comment,
    }


@router.get("/validated", response_model=AggregatedValidatedResponse)
async def get_validated_hostnames(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    application_name: Optional[str] = None,
    asset_owner: Optional[str] = None,
    validated_by: Optional[str] = None,
    sort_by: Optional[str] = Query("validated_at", pattern="^(validated_at|hostname|mc_criticality)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Base query components
    validation_alias = MorningChecklistValidation
    
    # If we are filtering by date, we likely want to see the history/specific records for that date range
    # rather than just the "latest ever" record for the host. 
    # So we strictly apply the "get latest" subquery ONLY if we are in "Current Status" mode (no date filters).
    
    is_historical_view = start_date is not None or end_date is not None

    if is_historical_view:
        # Direct query for history
        query = (
            db.query(
                MorningChecklistValidation,
                User.full_name,
                User.username,
                MorningChecklist.ip
            )
            .outerjoin(User, MorningChecklistValidation.validate_by == User.id)
            .outerjoin(MorningChecklist, and_(
                MorningChecklistValidation.hostname == MorningChecklist.hostname,
                MorningChecklistValidation.mc_check_date == MorningChecklist.mc_check_date
            ))
        )
    else:
        # "Current Snapshot" view - get the very latest validation for each hostname
        subquery = (
            db.query(
                MorningChecklistValidation.hostname.label("hostname"),
                func.max(MorningChecklistValidation.id).label("latest_id"),
            )
            .group_by(MorningChecklistValidation.hostname)
            .subquery()
        )

        query = (
            db.query(
                MorningChecklistValidation,
                User.full_name,
                User.username,
                MorningChecklist.ip
            )
            .join(
                subquery,
                (MorningChecklistValidation.id == subquery.c.latest_id),
            )
            .outerjoin(User, MorningChecklistValidation.validate_by == User.id)
            .outerjoin(MorningChecklist, and_(
                MorningChecklistValidation.hostname == MorningChecklist.hostname,
                MorningChecklistValidation.mc_check_date == MorningChecklist.mc_check_date
            ))
        )

    # Apply Filters
    if start_date:
        query = query.filter(MorningChecklistValidation.mc_check_date >= start_date)
    if end_date:
        query = query.filter(MorningChecklistValidation.mc_check_date <= end_date)
    
    if application_name:
        query = query.filter(MorningChecklistValidation.application_name == application_name)
    if asset_owner:
        query = query.filter(MorningChecklistValidation.asset_owner == asset_owner)
    if validated_by:
        query = query.filter(or_(User.username.ilike(f"%{validated_by}%"), User.full_name.ilike(f"%{validated_by}%")))


    if sort_by == "hostname":
        query = query.order_by(MorningChecklistValidation.hostname.asc())
    elif sort_by == "mc_criticality":
        query = query.order_by(MorningChecklistValidation.mc_criticality.desc().nullslast())
    else:
        query = query.order_by(MorningChecklistValidation.validated_at.desc())

    items: List[AggregatedValidatedHostname] = []
    for row, full_name, username, ip_addr in query.all():
        validator_name = full_name or username or f"User {row.validate_by}"
        items.append(
            AggregatedValidatedHostname(
                hostname=row.hostname,
                application_name=row.application_name,
                asset_owner=row.asset_owner,
                mc_criticality=row.mc_criticality,
                mc_check_date=row.mc_check_date,
                validated_at=row.validated_at,
                validate_by=validator_name,
                validate_comment=row.validate_comment,
                is_bulk=row.is_bulk,
                ip=ip_addr,
            )
        )
    
    return {"items": items}




@router.get("/hostnames/{hostname}/history", response_model=ValidationHistoryResponse)
async def get_validation_history(
    hostname: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(MorningChecklistValidation, User.full_name, User.username)
        .join(User, MorningChecklistValidation.validate_by == User.id)
        .filter(MorningChecklistValidation.hostname == hostname)
        .order_by(MorningChecklistValidation.validated_at.desc())
        .all()
    )
    return ValidationHistoryResponse(
        hostname=hostname,
        history=[
            ValidationHistoryItem(
                hostname=row.hostname,
                application_name=row.application_name,
                asset_owner=row.asset_owner,
                mc_criticality=row.mc_criticality,
                mc_check_date=row.mc_check_date,
                validated_at=row.validated_at,
                validate_by=full_name if full_name else username,
                validate_comment=row.validate_comment,
                is_bulk=row.is_bulk,
            )
            for row, full_name, username in rows
        ],
    )


@router.get("/export")
async def export_summary(
    date_param: date = Query(..., alias="date"),
    application_name: Optional[str] = None,
    asset_owner: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # UPDATED IMPORT
    from app.services.morning_checklist.report_generator import generate_morning_checklist_excel
    
    stream = generate_morning_checklist_excel(
        db=db,
        target_date=date_param,
        application_name=application_name,
        asset_owner=asset_owner
    )
    

    filename = f"checklist_export_{date_param}.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
