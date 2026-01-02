"""
End-to-end tests for IPAM (IP Address Management)
"""
import pytest
from fastapi import status
from app.models.user import User
from app.models.ipam import IpamSegment, IpamStatus
from app.core.security import create_access_token

@pytest.mark.e2e
class TestIpamE2E:
    """End-to-end tests for IPAM"""

    def test_complete_ipam_flow(self, client, test_db):
        """
        Test the complete IPAM workflow:
        1. Create Segment
        2. List Segments (Verify counts)
        3. Get Segment IPs (Verify auto-calc)
        4. Assign IP (Update status)
        5. Verify Audit Logs
        """
        # --- Setup User ---
        user = User(
            username="ipam_tester",
            email="ipam@example.com",
            is_active=True, 
            is_admin=True # Admin to ensure access
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        access_token = create_access_token({"sub": user.username, "user_id": user.id})
        headers = {"Authorization": f"Bearer {access_token}"}

        # --- 1. Create Segment (via API) ---
        segment_data = {
            "segment": "192.168.100.0/24",
            "name": "E2E Test LAN",
            "location": "Test Datacenter",
            "entity": "Test Corp",
            "environment": "Production",
            "network_zone": "DMZ",
            "description": "Created via E2E test",
            "segment_description": "Legacy segment"
        }
        
        response = client.post(
            "/api/v1/network/ipam/segments",
            json=segment_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        segment_id = data["id"]
        assert data["segment"] == segment_data["segment"]
        assert data["total_ips"] > 0
        # Should be 256 for /24 technically, but some logic might exclude network/broadcast
        # The implementation uses ip_network(..., strict=False).num_addresses which is 256
        assert data["total_ips"] == 256
        assert data["assigned_ips"] == 0

        # --- 2. List Segments ---
        response = client.get(
            "/api/v1/network/ipam/segments",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        list_data = response.json()
        assert len(list_data) >= 1
        # Find our segment
        our_seg = next((s for s in list_data if s["id"] == segment_id), None)
        assert our_seg is not None
        assert our_seg["assigned_ips"] == 0

        # --- 3. Get Segment IPs ---
        # Pick an IP to assign: 192.168.100.10
        target_ip = "192.168.100.10"
        
        response = client.get(
            f"/api/v1/network/ipam/segments/{segment_id}/ips",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        ips_data = response.json()
        
        # Verify target IP exists and is unassigned
        ip_entry = next((i for i in ips_data if i["ip_address"] == target_ip), None)
        assert ip_entry is not None
        assert ip_entry["status"] == "Unassigned"

        # --- 4. Assign IP ---
        allocation_payload = {
            "status": "Assigned",
            "ritm": "RITM1234567",
            "comment": "Assigned for E2E testing",
            "source": "Manual"
        }
        
        # The implementation uses POST /ips or similar. Let's check the IPAM API file again.
        # It has: @router.post("/ips") -> update_ip_allocation (which takes payload, segment_id, ip_address as QUERY/BODY?)
        # Wait, the signature was:
        # def update_ip_allocation(payload: IpamAllocationUpdate, segment_id: int, ip_address: str, ...)
        # And endpoint path was POST "/ips"
        # This implies segment_id and ip_address are query params? The snippet didn't show Query(...)
        # FastAPI defaults primitives to Query if not Path.
        # Let's double check the implementation seen in step 1294.
        
        # Line 208: @router.post("/ips", response_model=IpamIpResponse)
        # Line 209: def update_ip_allocation(payload: IpamAllocationUpdate, segment_id: int, ip_address: str, ...
        # Yes, segment_id and ip_address are Query parameters.
        # Wait, later in the file (Line 294) there is:
        # @router.put("/segments/{segment_id}/ips/{ip_address}")
        # def update_allocation(...)
        # Which one is the "primary" or "better" one? The PUT looks much more standard.
        # The POST /ips exists but PUT is cleaner.
        # I'll use the PUT one if it works, as it has path params.
        
        response = client.put(
            f"/api/v1/network/ipam/segments/{segment_id}/ips/{target_ip}",
            json=allocation_payload,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        alloc_resp = response.json()
        assert alloc_resp["status"] == "Assigned"
        assert alloc_resp["ritm"] == "RITM1234567"

        # --- 5. Verify Assignment in Details ---
        # Re-fetch IPs list
        response = client.get(
            f"/api/v1/network/ipam/segments/{segment_id}/ips",
            headers=headers
        )
        ips_data = response.json()
        ip_entry = next((i for i in ips_data if i["ip_address"] == target_ip), None)
        assert ip_entry["status"] == "Assigned"
        
        # Re-fetch Segments list (verify count increment)
        response = client.get(
            "/api/v1/network/ipam/segments",
            headers=headers
        )
        list_data = response.json()
        our_seg = next((s for s in list_data if s["id"] == segment_id), None)
        assert our_seg["assigned_ips"] == 1

        # --- 6. Verify Audit Logs ---
        response = client.get(
            f"/api/v1/network/ipam/audit-logs?segment_id={segment_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        logs = response.json()
        assert len(logs) >= 1
        latest_log = logs[0]
        assert latest_log["action"] == "ASSIGN_IP"
        assert target_ip in latest_log["ip_address"]
        assert "Assigned status: Assigned" in latest_log["changes"]
        assert latest_log["username"] == user.username
