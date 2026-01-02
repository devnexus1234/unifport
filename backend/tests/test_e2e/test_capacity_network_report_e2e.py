import pytest
from fastapi.testclient import TestClient
import pandas as pd
import io
from app.core.config import settings
from unittest.mock import patch, MagicMock

def test_capacity_network_report_flow(client: TestClient, normal_user_token_headers):
    """
    E2E Flow for Network Capacity Report:
    1. Create a zone in a region
    2. Add a device to that zone
    3. Check dashboard to see the device count
    4. Delete the device
    5. Check dashboard to see count decrease
    """
    
    # 1. Create Zone
    # Note: Using direct API calls
    zone_payload = {
        "region_name": "XYZ",
        "zone_name": "E2E Zone"
    }
    r = client.post(
        "/api/v1/capacity-network-report/zone-region-mapping/add",
        json=zone_payload,
        headers=normal_user_token_headers
    )
    assert r.status_code == 201, f"Failed to create zone: {r.text}"
    
    # 2. Add Device
    device_payload = {
        "zone_name": "E2E Zone",
        "device_name": "E2E Device"
    }
    r = client.post(
        "/api/v1/capacity-network-report/device-zone-mapping/add",
        json=device_payload,
        headers=normal_user_token_headers
    )
    assert r.status_code == 201, f"Failed to add device: {r.text}"
    
    # 3. Check Dashboard
    r = client.get(
        "/api/v1/capacity-network-report/dashboard",
        params={"region": "XYZ", "production_hours": True},
        headers=normal_user_token_headers
    )
    assert r.status_code == 200
    data = r.json()
    e2e_zone = next((z for z in data["zone_summary"] if z["zone_name"] == "E2E Zone"), None)
    assert e2e_zone is not None, "E2E Zone not found in dashboard"
    assert e2e_zone["total_device_count"] == 1
    
    # 4. Delete Device
    r = client.delete(
        "/api/v1/capacity-network-report/device-zone-mapping/delete",
        params={"zone_name": "E2E Zone", "device_name": "E2E Device"},
        headers=normal_user_token_headers
    )
    assert r.status_code == 200
    
    # 5. Check Dashboard Again
    r = client.get(
        "/api/v1/capacity-network-report/dashboard",
        params={"region": "XYZ", "production_hours": True},
        headers=normal_user_token_headers
    )
    assert r.status_code == 200
    data = r.json()
    e2e_zone = next((z for z in data["zone_summary"] if z["zone_name"] == "E2E Zone"), None)
    # The zone might still be there but count 0, or logic might exclude it if no devices? 
    # Current logic: get_zones_for_region gets all zones mapped to region.
    # Count should be 0.
    assert e2e_zone["total_device_count"] == 0


def test_upload_network_report(client: TestClient, normal_user_token_headers):
    # Create simple excel file content
    buffer = io.BytesIO(b"dummy excel content")
    # We patch the processing function to avoid Excel parsing errors with dummy content
    with patch("app.api.v1.capacity_network_report.process_capacity_network_files") as mock_process:
        files = {'network_data_file': ('test.xlsx', buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        response = client.post(
            f"/api/v1/capacity-network-report/upload", 
            headers=normal_user_token_headers, 
            files=files
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert "network_data_path" in data
        mock_process.assert_called_once()
