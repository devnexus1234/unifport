import pytest
from fastapi import status
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_ipam_service():
    with patch("app.api.v1.network.ipam.IpamService") as mock:
        yield mock

@pytest.mark.unit
def test_get_ipam_segments_unauthenticated(client):
    """Test that unauthenticated users cannot access IPAM segments"""
    response = client.get("/api/v1/network/ipam/segments")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.unit
def test_get_ipam_segments(client, test_db, normal_user_token_headers):
    """Test retrieving IPAM segments"""
    # Assuming seed data might be present or empty, but we check status 200
    response = client.get(
        "/api/v1/network/ipam/segments",
        headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.unit
def test_get_segment_details_not_found(client, normal_user_token_headers):
    """Test retrieving a non-existent segment"""
    response = client.get(
        "/api/v1/network/ipam/segments/99999",
        headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.unit
def test_get_audit_logs(client, normal_user_token_headers):
    """Test retrieving audit logs"""
    response = client.get(
        "/api/v1/network/ipam/audit-logs",
        headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.unit
def test_create_segment_invalid_cidr(client, normal_user_token_headers):
    """Test validation failure for invalid CIDR"""
    payload = {
        "segment": "999.999.999.999/24",
        "name": "Invalid Seg",
        "entity": "Test Entity"
    }
    response = client.post(
        "/api/v1/network/ipam/segments",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid CIDR" in response.json()["detail"]

@pytest.mark.unit
def test_update_allocation_invalid_ip(client, test_db, normal_user_token_headers):
    """Test updating allocation with IP outside segment"""
    # Mock finding segment vs checking IP logic
    # Ideally unit test mocks service/DB, but here we use client + test_db (semi-integration/unit)
    # We'll rely on the logic in api/v1/ipam.py
    
    # 1. Create valid segment
    from app.models.ipam import IpamSegment
    seg = IpamSegment(segment="10.0.0.0/24", name="Unit Test Seg", entity="Test Entity")
    test_db.add(seg)
    test_db.commit()
    
    # 2. Try to update IP that is NOT in 10.0.0.0/24
    payload = {"status": "Assigned"}
    response = client.put(
        f"/api/v1/network/ipam/segments/{seg.id}/ips/192.168.1.1",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "IP does not belong to segment" in response.json()["detail"]
