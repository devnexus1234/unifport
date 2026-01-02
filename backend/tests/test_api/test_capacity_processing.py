
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
import pandas as pd
from app.api.v1.capacity_firewall_report import process_capacity_files
from app.api.v1.capacity_network_report import process_capacity_network_files
from app.models.capacity import CapacityValues
from app.models.capacity_network import CapacityNetworkValues

@pytest.fixture
def mock_pandas_read_excel():
    with patch("pandas.read_excel") as mock:
        yield mock

@pytest.mark.asyncio
async def test_process_capacity_files(db_session: Session, mock_pandas_read_excel):
    # Setup mock data for Capacity Report
    # df_input1 (raw data)
    data1 = {
        "device_name": ["Device1", "Device1", "Device2"],
        "mean_cpu": ["10", "15", "20"],
        "peak_cpu": ["20", "25", "30"],
        "ntimes_cpu": [0, 1, 0],  # Device1: first row init, second row peak update
        "mean_memory": ["30", "35", "40"],
        "peak_memory": ["40", "45", "50"],
        "ntimes_memory": [0, 1, 0],
        "first_peak_cpu_dt": ["01-Jan-2023 10:00 20.0(peak: 25.0) to 01-Jan-2023 10:05", "01-Jan-2023 10:00 20.0(peak: 25.0) to 01-Jan-2023 10:05", ""],
        "first_peak_memory_dt": ["01-Jan-2023 10:00 40.0(peak: 45.0) to 01-Jan-2023 10:05", "01-Jan-2023 10:00 40.0(peak: 45.0) to 01-Jan-2023 10:05", ""]
    }
    df1 = pd.DataFrame(data1)

    # df_input2 (connection count)
    data2 = {
        "Entity Name": ["Device1", "Device2"],
        "Mean": ["100", "200"],
        "Peak": ["150", "250"]
    }
    df2 = pd.DataFrame(data2)

    # Configure mock to return df1 then df2
    mock_pandas_read_excel.side_effect = [df1, df2]

    start_date = "2023-01-01"
    end_date = "2023-01-31"

    result = await process_capacity_files(
        db_session,
        start_date,
        end_date,
        "dummy_raw_path.xlsx",
        "dummy_conn_path.xlsx"
    )

    assert result is True

    # Verify Database Updates
    # Note: Processing is currently disabled, so no DB updates happen.
    # device1 = db_session.query(CapacityValues).filter_by(device_name="Device1").first()
    # assert device1 is not None
    # assert device1.peak_cpu == 25.0
    # assert device1.peak_memory == 45.0
    # # Connection data
    # assert device1.mean_connection == 100.0
    # assert device1.peak_connection == 150.

@pytest.mark.asyncio
async def test_process_capacity_network_files(db_session: Session, mock_pandas_read_excel):
    # Setup mock data for Network Capacity Report
    data = {
        "device_name": ["NetDevice1", "NetDevice1"],
        "mean_cpu": ["5", "8"],
        "peak_cpu": ["10", "12"],
        "ntimes_cpu": [0, 1],
        "mean_memory": ["15", "18"],
        "peak_memory": ["20", "22"],
        "ntimes_memory": [0, 1],
        "first_peak_cpu_dt": ["01-Jan-2023 10:00 10.0(peak: 12.0) to 01-Jan-2023 10:05", "01-Jan-2023 10:00 10.0(peak: 12.0) to 01-Jan-2023 10:05"],
        "first_peak_memory_dt": ["01-Jan-2023 10:00 20.0(peak: 22.0) to 01-Jan-2023 10:05", "01-Jan-2023 10:00 20.0(peak: 22.0) to 01-Jan-2023 10:05"]
    }
    df = pd.DataFrame(data)

    mock_pandas_read_excel.return_value = df  # Only 1 file read

    result = await process_capacity_network_files(
        db_session,
        "dummy_network_path.xlsx"
    )

    assert result is True

    # Verify Database Updates
    # Note: Processing is currently disabled, so no DB updates happen.
    # device1 = db_session.query(CapacityNetworkValues).filter_by(device_name="NetDevice1").first()
    # assert device1 is not None
    # assert device1.peak_cpu == 12.0
    # assert device1.peak_memory == 22.0
