import pytest
from app.models.ipam import IpamSegment, IpamAllocation, IpamStatus
from app.models.user import User

@pytest.mark.integration
def test_ipam_full_flow(client, test_db, normal_user_token_headers):
    """
    Test a full flow:
    1. Create a segment (via DB directly as no POST endpoint for segment for now?)
       Wait, plan said "GET /ipam/segments". Does user create segments via API?
       The plan mentions POST /ipam/ips but for segments it says "View IP segments".
       Assuming segments are pre-seeded or created via different mechanism (maybe not implemented yet in this feature request).
       I'll create segment via DB.
    2. List segments -> verify total_ips.
    3. Get IPs -> verify all UNASSIGNED.
    4. Update IP (Assign) -> verify status and audit log.
    """
    
    # 1. Setup Segment
    segment = IpamSegment(
        segment="10.0.0.0/24",
        location="Test Loc",
        network_zone="Test Zone",
        entity="Test Entity",
        environment="Test Env",
        description="Integration Test Segment",
        name="TestSeg"
    )
    test_db.add(segment)
    test_db.commit()
    test_db.refresh(segment)
    
    segment_id = segment.id
    
    # 2. List Segments
    response = client.get("/api/v1/network/ipam/segments", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    target_seg = next(s for s in data if s["id"] == segment_id)
    assert target_seg["total_ips"] == 254
    assert target_seg["assigned_ips"] == 0
    
    # 3. Get IPs
    response = client.get(f"/api/v1/network/ipam/segments/{segment_id}/ips", headers=normal_user_token_headers)
    assert response.status_code == 200
    ips = response.json()
    # Check a random IP is unassigned
    assert ips[0]["status"] == "Unassigned"
    
    # 4. Assign an IP
    target_ip = "10.0.0.10"
    payload = {
        "status": "Assigned",
        "ritm": "RITM1234567",
        "comment": "Integration Test",
        "source": "Manual"
    }
    response = client.put(
        f"/api/v1/network/ipam/segments/{segment_id}/ips/{target_ip}", 
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    updated_ip = response.json()
    assert updated_ip["status"] == "Assigned"
    assert updated_ip["ritm"] == "RITM1234567"
    
    # 5. Verify Segments Count Update
    response = client.get("/api/v1/network/ipam/segments", headers=normal_user_token_headers)
    target_seg = next(s for s in response.json() if s["id"] == segment_id)
    assert target_seg["assigned_ips"] == 1
    
    # 6. Verify Audit Logs
    response = client.get(
        f"/api/v1/network/ipam/audit-logs?segment_id={segment_id}&ip_address={target_ip}",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "ASSIGN_IP"
    assert logs[0]["user_id"] is not None
    assert logs[0]["user_id"] is not None

@pytest.mark.integration
def test_ipam_segment_validation(client, normal_user_token_headers):
    """Test validation of invalid segment via API"""
    payload = {
        "segment": "invalid-cidr",
        "name": "Bad Seg",
        "location": "Nowhere", 
        "application_name": "Test"
    }
    # Assuming the previous implementation plan for CREATE via API is valid, 
    # and we have implemented data validation in schemas/models (which we did in unit test validation).
    response = client.post(
        "/api/v1/network/ipam/segments",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 400
    assert "Invalid CIDR" in response.json()["detail"]

@pytest.mark.integration
def test_ipam_ip_lifecycle(client, test_db, normal_user_token_headers):
    """
    Test IP Lifecycle: Assign -> Update -> Unassign
    """
    from app.models.ipam import IpamSegment
    # 1. Create Segment
    segment = IpamSegment(
        segment="192.168.200.0/24",
        name="Lifecycle Seg", 
        entity="Lifecycle Entity"
    )
    test_db.add(segment)
    test_db.commit()
    
    target_ip = "192.168.200.5"
    
    # 2. Assign
    payload_assign = {"status": "Assigned", "comment": "Initial"}
    response = client.put(
        f"/api/v1/network/ipam/segments/{segment.id}/ips/{target_ip}",
        json=payload_assign,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Assigned"
    
    # 3. Update
    payload_update = {"status": "Reserved", "comment": "Updated"}
    response = client.put(
        f"/api/v1/network/ipam/segments/{segment.id}/ips/{target_ip}",
        json=payload_update,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Reserved"
    
    # 4. Unassign (Update status to Unassigned)
    payload_unassign = {"status": "Unassigned", "comment": "Freed"}
    response = client.put(
        f"/api/v1/network/ipam/segments/{segment.id}/ips/{target_ip}",
        json=payload_unassign,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Unassigned"
