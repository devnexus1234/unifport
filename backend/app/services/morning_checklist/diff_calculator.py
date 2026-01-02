from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.morning_checklist import MorningChecklist
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def update_morning_checklist_diffs(db_session: Session = None):
    """
    Background task to calculate diff status for rows with NULL mc_diff_status.
    Compare D with D-1.
    """
    logger.info("Starting morning checklist diff calculation job")
    
    should_close = False
    if db_session:
        db = db_session
    else:
        db = SessionLocal()
        should_close = True
        
    try:
        # Get rows with null status
        # Order by date desc to process recent ones first? Or just all.
        pending_rows = db.query(MorningChecklist).filter(MorningChecklist.mc_diff_status == None).all()
        
        if not pending_rows:
            logger.info("No pending rows for diff calculation")
            return

        logger.info(f"Found {len(pending_rows)} pending rows")
        
        # We process them one by one or in batches.
        # Ideally, we should group by (hostname, date) to fetch prev data efficiently? 
        # But for simplicity, let's do one by one or simple map lookup if memory allows.
        
        count_updated = 0
        for row in pending_rows:
            # Find D-1
            prev_date = row.mc_check_date - timedelta(days=1)
            
            # Find matching prev row (same hostname, same command?)
            # Assuming 'commands' column is the differentiator if multiple rows per host.
            prev_row = db.query(MorningChecklist).filter(
                MorningChecklist.mc_check_date == prev_date,
                MorningChecklist.hostname == row.hostname,
                MorningChecklist.commands == row.commands
            ).first()
            
            status = "success" # Default if no diff or no history (as per requirements?) 
                               # "initially this will be null" -> user wants to update it.
            
            if not prev_row:
                 # No history -> is it success or just 'success' (no diff)?
                 # Usually if new, it's not a diff failure.
                 status = "success" 
            else:
                 # Compare output
                 cur_out = (row.mc_output or "").strip()
                 prev_out = (prev_row.mc_output or "").strip()
                 if cur_out == prev_out:
                     status = "success"
                 else:
                     status = "error" # or "failed"? Existing 'mc_status' is 'failed', diff usually implies 'error' in this app logic?
                                      # In summary logic: groups[key].error_count += 1 if diff exists.
            
            row.mc_diff_status = status
            count_updated += 1
            
            # Commit partially or at end? 
            # Commit every 100 rows?
            if count_updated % 100 == 0:
                db.commit()
        
        db.commit()
        logger.info(f"Updated {count_updated} rows with diff status.")
        
    except Exception as e:
        logger.error(f"Error in diff calculation job: {e}")
        db.rollback()
    finally:
        if should_close:
            db.close()
