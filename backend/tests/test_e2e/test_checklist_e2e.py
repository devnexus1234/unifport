"""
End-to-end tests for Morning Checklist
"""
import pytest
from datetime import date, timedelta
from fastapi import status
from app.models.user import User
from app.models.morning_checklist import MorningChecklist
from app.core.security import create_access_token

@pytest.mark.e2e
class TestChecklistE2E:
    """End-to-end tests for Checklist"""

    def test_checklist_flow(self, client, test_db):
        """
        Test the complete Checklist workflow:
        1. Seed Data (Yesterday & Today)
        2. Get Dashboard Dates
        3. Get Summary (Verify diff logic)
        4. Validate Hostname
        5. Verify Status
        6. Undo Validation
        """
        # --- Setup User ---
        user = User(
            username="checklist_tester",
            email="check@example.com",
            is_active=True, 
            is_admin=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        access_token = create_access_token({"sub": user.username, "user_id": user.id})
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # --- 1. Seed Data ---
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Scenario: Host 'web-01' has changes (Diff)
        # Yesterday: "UP"
        # Today: "DOWN"
        
        row_prev = MorningChecklist(
            hostname="web-01",
            application_name="Web App",
            asset_owner="Team A",
            mc_check_date=yesterday,
            commands="check_status",
            mc_output="UP",
            mc_status="reachable",
            mc_criticality="High"
        )
        test_db.add(row_prev)
        
        row_curr = MorningChecklist(
            hostname="web-01",
            application_name="Web App",
            asset_owner="Team A",
            mc_check_date=today,
            commands="check_status",
            mc_output="DOWN", # Change!
            mc_status="reachable",
            mc_criticality="High"
        )
        test_db.add(row_curr)
        
        # Scenario: Host 'db-01' has no changes (No Diff)
        row_db_prev = MorningChecklist(
            hostname="db-01",
            application_name="DB App",
            asset_owner="Team B",
            mc_check_date=yesterday,
            commands="iostat",
            mc_output="OK",
            mc_status="reachable"
        )
        test_db.add(row_db_prev)
        
        row_db_curr = MorningChecklist(
            hostname="db-01",
            application_name="DB App",
            asset_owner="Team B",
            mc_check_date=today,
            commands="iostat",
            mc_output="OK", # No Change
            mc_status="reachable"
        )
        test_db.add(row_db_curr)

        test_db.commit()

        # --- 2. Get Dates ---
        response = client.get(
            "/api/v1/linux/morning-checklist/dates",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        dates = response.json()
        assert today.isoformat() in dates
        assert yesterday.isoformat() in dates

        # --- 3. Get Summary (Verify Diffs) ---
        response = client.get(
            f"/api/v1/linux/morning-checklist/summary?date={today.isoformat()}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        summary = response.json()
        
        # Find group for Web App (Should have 1 error count due to Diff)
        web_group = next((g for g in summary["groups"] if g["application_name"] == "Web App"), None)
        assert web_group is not None
        # web-01 changed from UP to DOWN, so it should be flagged as error (diff found)
        assert web_group["error_count"] == 1 
        
        # Find group for DB App (Should be success)
        db_group = next((g for g in summary["groups"] if g["application_name"] == "DB App"), None)
        assert db_group is not None
        assert db_group["success_count"] == 1
        assert db_group["error_count"] == 0

        # --- 4. Get Details & Verify Diff Content ---
        response = client.get(
            f"/api/v1/linux/morning-checklist/hostnames/web-01/diff?date={today.isoformat()}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        diffs = response.json()
        assert len(diffs) > 0
        cmd_diff = diffs[0]
        assert cmd_diff["command"] == "check_status"
        assert cmd_diff["current_output"] == "DOWN"
        assert cmd_diff["previous_output"] == "UP"
        
        # --- 5. Validate Hostname ---
        validation_payload = {
            "validate_comment": "Acknowledged downtime",
            "is_bulk": False
        }
        response = client.post(
            f"/api/v1/linux/morning-checklist/hostnames/web-01/validate?date={today.isoformat()}",
            json=validation_payload,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify validation history
        response = client.get(
            f"/api/v1/linux/morning-checklist/hostnames/web-01/history",
            headers=headers
        )
        history = response.json()
        assert len(history["history"]) >= 1
        assert history["history"][0]["validate_comment"] == "Acknowledged downtime"
        
        # Verify Summary again - Web App should now show success because it is validated
        response = client.get(
            f"/api/v1/linux/morning-checklist/summary?date={today.isoformat()}",
            headers=headers
        )
        summary = response.json()
        web_group = next((g for g in summary["groups"] if g["application_name"] == "Web App"), None)
        # Validation overrides diff status -> counts as success
        assert web_group["success_count"] == 1
        
        # --- 6. Undo Validation ---
        response = client.delete(
            f"/api/v1/linux/morning-checklist/hostnames/web-01/validate?date={today.isoformat()}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify it reverted to error
        response = client.get(
            f"/api/v1/linux/morning-checklist/summary?date={today.isoformat()}",
            headers=headers
        )
        summary = response.json()
        web_group = next((g for g in summary["groups"] if g["application_name"] == "Web App"), None)
        assert web_group["error_count"] == 1

