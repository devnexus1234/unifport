"""
Integration tests for Morning Checklist
"""
import pytest
from datetime import date, timedelta
from app.models.user import User
from app.models.morning_checklist import MorningChecklist, MorningChecklistValidation

@pytest.mark.integration
def test_checklist_dashboard_integration(client, test_db, normal_user_token_headers):
    """
    Test Dashboard aggregation with real DB calls and filters
    """
    today = date(2023, 5, 1)
    yesterday = today - timedelta(days=1)
    
    # 1. Seed Data
    # Host 1: No Change (Success)
    test_db.add(MorningChecklist(
        hostname="int-host-1", application_name="App A", asset_owner="Owner A",
        mc_check_date=yesterday, commands="TEST", mc_output="OK", mc_status="reachable"
    ))
    test_db.add(MorningChecklist(
        hostname="int-host-1", application_name="App A", asset_owner="Owner A",
        mc_check_date=today, commands="TEST", mc_output="OK", mc_status="reachable"
    ))
    
    # Host 2: Change (Error)
    test_db.add(MorningChecklist(
        hostname="int-host-2", application_name="App A", asset_owner="Owner A",
        mc_check_date=yesterday, commands="TEST", mc_output="OK", mc_status="reachable"
    ))
    test_db.add(MorningChecklist(
        hostname="int-host-2", application_name="App A", asset_owner="Owner A",
        mc_check_date=today, commands="TEST", mc_output="FAIL", mc_status="failed"
    ))
    test_db.commit()

    # 2. Get Summary 
    response = client.get(
        f"/api/v1/linux/morning-checklist/summary?date={today.isoformat()}",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    group = next(g for g in data["groups"] if g["application_name"] == "App A")
    
    # Check counts
    # host-1 ok -> success, host-2 fail -> error
    assert group["success_count"] == 1
    assert group["error_count"] == 1
    assert data["reachability"]["failed"] == 1
    assert data["reachability"]["reachable"] == 1


@pytest.mark.integration
def test_validation_persistence(client, test_db, normal_user_token_headers):
    """
    Test persistence of validation flags
    """
    today = date(2023, 5, 2)
    hostname = "persist-host"
    
    row = MorningChecklist(
        hostname=hostname,
        application_name="App P",
        mc_check_date=today,
        mc_output="FAIL",
        mc_status="failed"
    )
    test_db.add(row)
    test_db.commit()
    
    # 1. Validate
    payload = {"validate_comment": "Fixing it"}
    client.post(
        f"/api/v1/linux/morning-checklist/hostnames/{hostname}/validate?date={today.isoformat()}",
        json=payload,
        headers=normal_user_token_headers
    )
    
    # 2. Check DB directly (persistence check)
    test_db.expire_all()
    # Need to query fresh
    db_row = test_db.query(MorningChecklist).filter_by(hostname=hostname, mc_check_date=today).first()
    assert db_row.is_validated is True
    
    # 3. Check History
    history_row = test_db.query(MorningChecklistValidation).filter_by(hostname=hostname).first()
    assert history_row is not None
    assert history_row.validate_comment == "Fixing it"


@pytest.mark.integration
def test_bulk_validation(client, test_db, normal_user_token_headers):
    """
    Test bulk validation via API
    """
    today = date(2023, 5, 3)
    
    # Create 2 failed hosts for same app
    row1 = MorningChecklist(
       hostname="bulk-1", application_name="App B", mc_check_date=today, mc_status="failed"
    )
    row2 = MorningChecklist(
       hostname="bulk-2", application_name="App B", mc_check_date=today, mc_status="failed"
    )
    # Different app (should not be validated)
    row3 = MorningChecklist(
       hostname="bulk-3", application_name="App C", mc_check_date=today, mc_status="failed"
    )
    
    test_db.add_all([row1, row2, row3])
    test_db.commit()
    
    payload = {
        "date": today.isoformat(),
        "application_name": "App B",
        "validate_comment": "Bulk OK"
    }
    
    response = client.post(
        "/api/v1/linux/morning-checklist/validate-all",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["count"] == 2
    
    # Verify logic
    test_db.expire_all()
    valid_rows = test_db.query(MorningChecklist).filter(
        MorningChecklist.mc_check_date == today,
        MorningChecklist.is_validated == True
    ).all()
    assert len(valid_rows) == 2
    hostnames = [r.hostname for r in valid_rows]
    assert "bulk-1" in hostnames
    assert "bulk-2" in hostnames
    assert "bulk-3" not in hostnames
