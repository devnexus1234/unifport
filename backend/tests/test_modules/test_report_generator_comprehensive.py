"""
Comprehensive tests for report generator to reach 75% coverage
"""
import pytest
from datetime import date, timedelta
from io import BytesIO
from app.services.morning_checklist.report_generator import generate_morning_checklist_excel
from app.models.morning_checklist import MorningChecklist

@pytest.mark.unit
class TestReportGeneratorComprehensive:
    """Comprehensive tests for report generator"""
    
    def test_generate_excel_with_data(self, test_db):
        """Test generating Excel with actual data"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Create current data
        mc_today = MorningChecklist(
            hostname="testhost",
            mc_check_date=today,
            application_name="TestApp",
            asset_owner="TestOwner",
            ip="192.168.1.1",
            commands="ps aux",
            mc_output="output_today",
            mc_status="reachable"
        )
        
        # Create previous data
        mc_yesterday = MorningChecklist(
            hostname="testhost",
            mc_check_date=yesterday,
            application_name="TestApp",
            asset_owner="TestOwner",
            ip="192.168.1.1",
            commands="ps aux",
            mc_output="output_yesterday",
            mc_status="reachable"
        )
        
        test_db.add_all([mc_today, mc_yesterday])
        test_db.commit()
        
        # Generate Excel
        stream = generate_morning_checklist_excel(test_db, today)
        
        assert isinstance(stream, BytesIO)
        assert stream.tell() == 0  # Should be at start
        content = stream.read()
        assert len(content) > 0
    
    def test_generate_excel_with_diff(self, test_db):
        """Test generating Excel with differences"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        mc_today = MorningChecklist(
            hostname="diffhost",
            mc_check_date=today,
            commands="ls -la",
            mc_output="file1\nfile2\nfile3",
            mc_status="reachable",
            application_name="DiffApp",
            ip="192.168.1.2"
        )
        
        mc_yesterday = MorningChecklist(
            hostname="diffhost",
            mc_check_date=yesterday,
            commands="ls -la",
            mc_output="file1\nfile2",
            mc_status="reachable",
            application_name="DiffApp",
            ip="192.168.1.2"
        )
        
        test_db.add_all([mc_today, mc_yesterday])
        test_db.commit()
        
        stream = generate_morning_checklist_excel(test_db, today)
        assert isinstance(stream, BytesIO)
        content = stream.read()
        assert len(content) > 0
    
    def test_generate_excel_no_previous_data(self, test_db):
        """Test generating Excel when no previous data exists"""
        today = date.today()
        
        mc = MorningChecklist(
            hostname="newhost",
            mc_check_date=today,
            commands="uptime",
            mc_output="up 5 days",
            mc_status="reachable",
            application_name="NewApp",
            ip="192.168.1.3"
        )
        
        test_db.add(mc)
        test_db.commit()
        
        stream = generate_morning_checklist_excel(test_db, today)
        assert isinstance(stream, BytesIO)
        content = stream.read()
        assert len(content) > 0
    
    def test_generate_excel_with_filters(self, test_db):
        """Test generating Excel with application and owner filters"""
        today = date.today()
        
        mc1 = MorningChecklist(
            hostname="filterhost1",
            mc_check_date=today,
            application_name="FilterApp",
            asset_owner="FilterOwner",
            commands="cmd1",
            mc_output="output1",
            mc_status="reachable",
            ip="192.168.1.4"
        )
        
        mc2 = MorningChecklist(
            hostname="filterhost2",
            mc_check_date=today,
            application_name="OtherApp",
            asset_owner="OtherOwner",
            commands="cmd2",
            mc_output="output2",
            mc_status="reachable",
            ip="192.168.1.5"
        )
        
        test_db.add_all([mc1, mc2])
        test_db.commit()
        
        # Filter by application
        stream = generate_morning_checklist_excel(test_db, today, application_name="FilterApp")
        assert isinstance(stream, BytesIO)
        
        # Filter by owner
        stream = generate_morning_checklist_excel(test_db, today, asset_owner="FilterOwner")
        assert isinstance(stream, BytesIO)
    
    def test_generate_excel_empty_data(self, test_db):
        """Test generating Excel with no data"""
        today = date.today()
        
        stream = generate_morning_checklist_excel(test_db, today)
        assert isinstance(stream, BytesIO)
        content = stream.read()
        assert len(content) > 0  # Should still have headers
    
    def test_generate_excel_null_values(self, test_db):
        """Test generating Excel with null values"""
        today = date.today()
        
        mc = MorningChecklist(
            hostname="nullhost",
            mc_check_date=today,
            application_name="NullApp",  # Required field
            commands=None,
            mc_output=None,
            mc_status="reachable",
            asset_owner=None,
            ip=None
        )
        
        test_db.add(mc)
        test_db.commit()
        
        stream = generate_morning_checklist_excel(test_db, today)
        assert isinstance(stream, BytesIO)
        content = stream.read()
        assert len(content) > 0
    
    def test_generate_excel_multiple_commands(self, test_db):
        """Test generating Excel with multiple commands for same host"""
        today = date.today()
        
        mc1 = MorningChecklist(
            hostname="multihost",
            mc_check_date=today,
            commands="cmd1",
            mc_output="output1",
            mc_status="reachable",
            application_name="MultiApp",
            ip="192.168.1.6"
        )
        
        mc2 = MorningChecklist(
            hostname="multihost",
            mc_check_date=today,
            commands="cmd2",
            mc_output="output2",
            mc_status="reachable",
            application_name="MultiApp",
            ip="192.168.1.6"
        )
        
        test_db.add_all([mc1, mc2])
        test_db.commit()
        
        stream = generate_morning_checklist_excel(test_db, today)
        assert isinstance(stream, BytesIO)
        content = stream.read()
        assert len(content) > 0

pytest_plugins = ["tests.fixtures.auth_fixtures"]
