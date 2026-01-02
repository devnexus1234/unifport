import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.morning_checklist import MorningChecklist, MorningChecklistValidation
from app.models.user import User
from app.core.config import settings

API_V1_STR = "/api/v1"

def test_validate_selected_success(client: TestClient, test_db: Session, normal_user_token_headers):
    # Setup
    check_date = date(2025, 1, 1)
    # Create test data
    row1 = MorningChecklist(
        hostname="host1",
        application_name="App1",
        mc_check_date=check_date,
        mc_status="unreachable",
        is_validated=False
    )
    row2 = MorningChecklist(
        hostname="host2",
        application_name="App1",
        mc_check_date=check_date,
        mc_status="failed",
        is_validated=False
    )
    test_db.add(row1)
    test_db.add(row2)
    test_db.commit()

    payload = {
        "date": str(check_date),
        "hostnames": ["host1", "host2"],
        "comment": "Bulk validating"
    }

    response = client.post(
        "/api/v1/linux/morning-checklist/validate-selected",
        json=payload,
        headers=normal_user_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "validated_selected"
    assert data["count"] == 2

    # Verify db updates
    test_db.refresh(row1)
    test_db.refresh(row2)
    assert row1.is_validated is True
    assert row2.is_validated is True

    # Verify validation entries
    validations = test_db.query(MorningChecklistValidation).filter(
        MorningChecklistValidation.mc_check_date == check_date
    ).all()
    assert len(validations) == 2
    assert validations[0].validate_comment == "Bulk validating"
    assert validations[0].is_bulk is True

def test_validate_selected_partial_missing(client: TestClient, test_db: Session, normal_user_token_headers):
    # Setup
    check_date = date(2025, 1, 2)
    row1 = MorningChecklist(
        hostname="hostA",
        application_name="App1",
        mc_check_date=check_date,
        is_validated=False
    )
    test_db.add(row1)
    test_db.commit()

    payload = {
        "date": str(check_date),
        "hostnames": ["hostA", "missing_host"],
        "comment": "Partial"
    }

    # The API currently validates found records and ignores missing ones? 
    # Logic in API: `rows = ... filter(hostname.in_(payload.hostnames))`
    # `targets = rows.all()`
    # If targets is empty, 404. If not empty, it validates what it finds.
    # It does NOT check if ALL requested hostnames are found, standard behavior usually validates what exists or fails all.
    # The current implementation validates what matches the filter.
    
    response = client.post(
        "/api/v1/linux/morning-checklist/validate-selected",
        json=payload,
        headers=normal_user_token_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1 # Only 1 found

    test_db.refresh(row1)
    assert row1.is_validated is True

def test_validate_selected_none_found(client: TestClient, test_db: Session, normal_user_token_headers):
    check_date = date(2025, 1, 3)
    payload = {
        "date": str(check_date),
        "hostnames": ["ghost_host"],
        "comment": "Fail"
    }
    response = client.post(
        "/api/v1/linux/morning-checklist/validate-selected",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 404

@pytest.mark.unit
def test_validate_selected_empty_list(test_db, client, normal_user_token_headers):
    """Test validating with empty hostname list"""
    today = date.today()
    payload = {
        "date": today.isoformat(),
        "hostnames": []
    }
    response = client.post(
        f"{API_V1_STR}/linux/morning-checklist/validate-selected",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 400


@pytest.mark.unit
def test_validate_groups_success(test_db, client, normal_user_token_headers):
    """Test successful bulk validation of groups"""
    today = date.today()
    
    # Create test data
    row1 = MorningChecklist(
        mc_check_date=today,
        hostname="host1",
        application_name="App1",
        asset_owner="Owner1",
        mc_status="unreachable",
        is_validated=False
    )
    row2 = MorningChecklist(
        mc_check_date=today,
        hostname="host2",
        application_name="App1",
        asset_owner="Owner1",
        mc_status="reachable",
        mc_diff_status="DIFF_FOUND",
        is_validated=False
    )
    # Different group
    row3 = MorningChecklist(
        mc_check_date=today,
        hostname="host3",
        application_name="App2",
        asset_owner="Owner2",
        mc_status="unreachable",
        is_validated=False
    )
    
    test_db.add_all([row1, row2, row3])
    test_db.commit()

    payload = {
        "date": today.isoformat(),
        "groups": [
            {"application_name": "App1", "asset_owner": "Owner1", "success_count": 0, "error_count": 0}
        ],
        "comment": "Group validation test"
    }

    response = client.post(
        f"{API_V1_STR}/linux/morning-checklist/validate-groups", 
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "validated_groups"
    assert data["count"] == 2  # host1 and host2

    # Verify rows updated
    test_db.refresh(row1)
    test_db.refresh(row2)
    test_db.refresh(row3)
    assert row1.is_validated is True
    assert row2.is_validated is True
    assert row3.is_validated is False  # Not in selected group


@pytest.mark.unit
def test_validate_groups_missing(test_db, client, normal_user_token_headers):
    """Test validate groups request 400 if groups missing"""
    today = date.today()
    payload = {
        "date": today.isoformat(),
        "groups": []
    }
    response = client.post(
        f"{API_V1_STR}/linux/morning-checklist/validate-groups",
        json=payload,
        headers=normal_user_token_headers
    )
    assert response.status_code == 400
