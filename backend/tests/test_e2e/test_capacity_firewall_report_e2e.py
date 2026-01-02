import pytest
from fastapi.testclient import TestClient
import io
from unittest.mock import patch, MagicMock

def test_capacity_report_flow(client: TestClient, normal_user_token_headers):
    """
    E2E Flow for Capacity Report:
    1. Create a zone in a region
    2. Add a device to that zone
    3. Check dashboard to see the device count
    4. Delete the device
    5. Check dashboard to see count decrease
    """
    
    # 1. Create Zone
    zone_payload = {
        "region_name": "XYZ",
        "zone_name": "E2E Cap Zone"
    }
    r = client.post(
        "/api/v1/capacity-firewall-report/zone-region-mapping/add",
        json=zone_payload,
        headers=normal_user_token_headers
    )
    assert r.status_code == 201, f"Failed to create zone: {r.text}"
    
    # 2. Add Device
    device_payload = {
        "zone_name": "E2E Cap Zone",
        "device_name": "E2E Cap Device"
    }
    r = client.post(
        "/api/v1/capacity-firewall-report/device-zone-mapping/add",
        json=device_payload,
        headers=normal_user_token_headers
    )
    assert r.status_code == 201, f"Failed to add device: {r.text}"
    
    # 3. Check Dashboard
    r = client.get(
        "/api/v1/capacity-firewall-report/dashboard",
        params={"region": "XYZ", "production_hours": True},
        headers=normal_user_token_headers
    )
    assert r.status_code == 200
    data = r.json()
    e2e_zone = next((z for z in data["zone_summary"] if z["zone_name"] == "E2E Cap Zone"), None)
    assert e2e_zone is not None, "E2E Zone not found in dashboard"
    assert e2e_zone["total_device_count"] == 1
    
    # 4. Delete Device
    r = client.delete(
        "/api/v1/capacity-firewall-report/device-zone-mapping/delete",
        params={"zone_name": "E2E Cap Zone", "device_name": "E2E Cap Device"},
        headers=normal_user_token_headers
    )
    assert r.status_code == 200
    
    # 5. Check Dashboard Again
    r = client.get(
        "/api/v1/capacity-firewall-report/dashboard",
        params={"region": "XYZ", "production_hours": True},
        headers=normal_user_token_headers
    )
    assert r.status_code == 200
    data = r.json()
    e2e_zone = next((z for z in data["zone_summary"] if z["zone_name"] == "E2E Cap Zone"), None)
    assert e2e_zone["total_device_count"] == 0

def test_upload_capacity_report(client: TestClient, normal_user_token_headers):
    # Create simple excel file content
    buffer = io.BytesIO(b"dummy excel content")
    # We patch the processing function to avoid Excel parsing errors with dummy content
    with patch("app.api.v1.capacity_firewall_report.process_capacity_files") as mock_process:
        files = {
            'raw_data_file': ('raw.xlsx', buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            'connection_count_file': ('conn.xlsx', io.BytesIO(b"dummy conn"), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        data = {
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        response = client.post(
            f"/api/v1/capacity-firewall-report/upload", 
            headers=normal_user_token_headers, 
            files=files,
            data=data
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        resp_data = response.json()
        assert "raw_data_path" in resp_data
        mock_process.assert_called_once()
