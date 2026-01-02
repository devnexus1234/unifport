import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from app.services.ipam_sync import sync_ipam_segments, SyncManager
from app.models.ipam import IpamSegment
from app.core.config import settings
from app.services.servicenow import ServiceNowClient

@pytest.mark.asyncio
async def test_ipam_sync_logic(db_session: Session):
    # Reset SyncManager
    SyncManager._instance = None
    # Mock data from ServiceNow
    mock_segments = [
        {
            "segment": "10.10.10.0/24",
            "name": "Test Segment 1",
            "description": "Synced from SNOW",
            "location": "Datacenter A",
            "entity": "Finance",
            "environment": "Prod",
            "network_zone": "DMZ",
            "segment_description": "Detailed desc 1"
        },
        {
            "segment": "192.168.1.0/24",
            "name": "Test Segment 2",
            "description": "Legacy Segment",
            "location": "Office B",
            "entity": "HR",
            "environment": "Dev",
            "network_zone": "Internal",
            "segment_description": "Detailed desc 2"
        }
    ]

    # Mock the snow_client.fetch_table_data method
    with patch("app.services.ipam_sync.snow_client.fetch_table_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_segments
        
        # Run sync
        result = await sync_ipam_segments(db=db_session)
        
        # Verify result stats
        assert result["total"] == 2
        assert result["synced"] == 2
        assert result["errors"] == 0
        
        # Verify DB content
        seg1 = db_session.query(IpamSegment).filter(IpamSegment.segment == "10.10.10.0/24").first()
        assert seg1 is not None
        assert seg1.name == "Test Segment 1"
        assert seg1.entity == "Finance"
        
        seg2 = db_session.query(IpamSegment).filter(IpamSegment.segment == "192.168.1.0/24").first()
        assert seg2 is not None
        assert seg2.environment == "Dev"

@pytest.mark.asyncio
async def test_ipam_sync_update_existing(db_session: Session):
    # Create existing segment
    existing = IpamSegment(
        segment="10.20.20.0/24",
        name="Old Name",
        entity="Old Entity"
    )
    db_session.add(existing)
    db_session.commit()
    
    # Mock update data
    mock_segments = [
        {
            "segment": "10.20.20.0/24",
            "name": "New Name",
            "entity": "New Entity",
            "location": "New Location"
        }
    ]
    
    with patch("app.services.ipam_sync.snow_client.fetch_table_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_segments
        
        await sync_ipam_segments(db=db_session)
        
        # Verify update
        updated = db_session.query(IpamSegment).filter(IpamSegment.segment == "10.20.20.0/24").first()
        assert updated.name == "New Name"
        assert updated.entity == "New Entity"
        assert updated.location == "New Location"
