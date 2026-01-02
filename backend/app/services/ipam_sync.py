from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.ipam import IpamSegment
from app.services.servicenow import snow_client
from app.core.config import settings
from app.core.logging_config import get_logger
import logging

from datetime import datetime, timezone

logger = get_logger(__name__)

class SyncManager:
    _instance = None
    
    def __init__(self):
        self.is_running = False
        self.last_run = None
        self.status = "IDLE" # IDLE, RUNNING, COMPLETED, FAILED
        self.result = {}
        self.error = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start_sync(self):
        self.is_running = True
        self.status = "RUNNING"
        self.error = None
        self.result = {}

    def complete_sync(self, result):
        self.is_running = False
        self.status = "COMPLETED"
        self.last_run = datetime.now(timezone.utc)
        self.result = result

    def fail_sync(self, error):
        self.is_running = False
        self.status = "FAILED"
        self.last_run = datetime.now(timezone.utc)
        self.error = str(error)

sync_manager = SyncManager.get_instance()

async def sync_ipam_segments(db: Session = None):
    """
    Sync IPAM segments from ServiceNow to local DB.
    
    Args:
        db: Optional database session. If not provided, a new one is created.
    """
    # Prevent concurrent runs if triggered manually via background task, 
    # though job scheduler might trigger it too. 
    # Validating here is good safety but mainly relevant for the API trigger.
    # The SyncManager is used primarily for UI feedback.
    
    manager = SyncManager.get_instance()
    # Note: If called by scheduler, we might want to just log it. 
    # If called by API, we want to track it.
    # Since this function is the worker, allow updating state regardless of source.
    
    manager.start_sync()
    logger.info("Starting IPAM Segment Sync")
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        # Fetch using new generic method
        # Page size and limit can be configurable if needed, using defaults for now
        segments_data = await snow_client.fetch_table_data(
            table=settings.SNOW_IPAM_TABLE,
            page_size=1000,
            max_pages=None # Fetch all
        )
        logger.info(f"Fetched {len(segments_data)} segments from ServiceNow table {settings.SNOW_IPAM_TABLE}")
        
        synced_count = 0
        error_count = 0
        
        for item in segments_data:
            try:
                # Map ServiceNow fields to IpamSegment model
                # Assuming SNOW keys match our columns closely or as per requirements
                # Basic mapping:
                cidr = item.get("segment") or item.get("u_segment") or item.get("cidr")
                if not cidr:
                    logger.warning(f"Skipping item without segment/cidr: {item}")
                    continue
                    
                segment_identifier = cidr.strip()
                
                # Check existance
                existing = db.query(IpamSegment).filter(IpamSegment.segment == segment_identifier).first()
                
                if existing:
                    # Update
                    existing.name = item.get("name", existing.name)
                    existing.description = item.get("description", existing.description)
                    existing.location = item.get("location", existing.location)
                    existing.entity = item.get("entity", existing.entity)
                    existing.environment = item.get("environment", existing.environment)
                    existing.network_zone = item.get("network_zone", existing.network_zone)
                    existing.segment_description = item.get("segment_description", existing.segment_description)
                else:
                    # Create
                    new_seg = IpamSegment(
                        segment=segment_identifier,
                        name=item.get("name"),
                        description=item.get("description"),
                        location=item.get("location"),
                        entity=item.get("entity"),
                        environment=item.get("environment"),
                        network_zone=item.get("network_zone"),
                        segment_description=item.get("segment_description")
                    )
                    db.add(new_seg)
                
                synced_count += 1
                
            except Exception as e:
                logger.error(f"Error syncing item {item}: {e}")
                error_count += 1
                
        db.commit()
        db.commit()
        logger.info(f"IPAM Segment Sync Completed. Synced: {synced_count}, Errors: {error_count}")
        result = {"total": len(segments_data), "synced": synced_count, "errors": error_count}
        manager.complete_sync(result)
        return result
        
    except Exception as e:
        logger.error(f"IPAM Segment Sync Failed: {e}")
        manager.fail_sync(e)
        raise
    finally:
        if close_db:
            db.close()
