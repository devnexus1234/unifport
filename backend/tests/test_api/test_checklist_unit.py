"""
Unit tests for Checklist Service Logic
"""
import pytest
from datetime import date
from unittest.mock import MagicMock
from app.models.morning_checklist import MorningChecklist
from app.api.v1.linux.morning_checklist.api import _compare_host, _build_host_maps

@pytest.mark.unit
def test_compare_host_logic_change_detected():
    """Test standard diff detection"""
    # Prev: "A", Curr: "B" -> Fail
    row_prev = MorningChecklist(
        mc_check_date=date(2023, 1, 1),
        commands="cmd1",
        mc_output="Output A",
        is_validated=False
    )
    row_curr = MorningChecklist(
        mc_check_date=date(2023, 1, 2),
        commands="cmd1",
        mc_output="Output B",
        is_validated=False
    )
    
    is_success, diffs = _compare_host([row_curr], [row_prev], return_all=True)
    
    assert is_success is False
    assert len(diffs) == 1
    assert diffs[0].command == "cmd1"
    assert diffs[0].current_output == "Output B"
    assert diffs[0].previous_output == "Output A"
    assert len(diffs[0].diff) > 0 # Should have diff lines

@pytest.mark.unit
def test_compare_host_logic_no_change():
    """Test no diff detection"""
    # Prev: "A", Curr: "A" -> Success
    row_prev = MorningChecklist(commands="cmd1", mc_output="A", is_validated=False)
    row_curr = MorningChecklist(commands="cmd1", mc_output="A", is_validated=False)
    
    is_success, diffs = _compare_host([row_curr], [row_prev], return_all=True)
    
    assert is_success is True
    # In return_all=True logic, it returns the items but with empty diff list
    assert diffs[0].diff == [] 

@pytest.mark.unit
def test_compare_host_logic_validated():
    """Test validation override"""
    # Prev: "A", Curr: "B" (Diff) BUT Validated -> Success
    row_prev = MorningChecklist(commands="cmd1", mc_output="A", is_validated=False)
    row_curr = MorningChecklist(commands="cmd1", mc_output="B", is_validated=True)
    
    is_success, diffs = _compare_host([row_curr], [row_prev])
    
    assert is_success is True

@pytest.mark.unit
def test_compare_host_logic_no_prev_data():
    """Test behavior when no previous data exists"""
    # No Prev -> Treated as "No data found" but Success if not validated? 
    # Logic says: if not prev_rows -> return True, [] (if not return_all)
    row_curr = MorningChecklist(commands="cmd1", mc_output="A", is_validated=False)
    
    is_success, diffs = _compare_host([row_curr], [])
    assert is_success is True
    assert diffs == []
