# Firewall Backup Logs Dashboard

## Overview
The **Firewall Backup Logs Dashboard** is a specialized module designed to monitor and report the status of firewall configuration backups. It provides insights into daily backup tasks, highlighting successful and failed backups across various devices (Checkpoint, Cisco ASA/FTD, F5, etc.). The dashboard aims to give administrators a quick "at-a-glance" view of backup health and detailed logs for troubleshooting.

## Functionalities
- **Daily Reporting**: View backup tasks executed on a specific date.
- **Summary Statistics**: Real-time aggregation of total devices backed up, success counts, and failure counts for the current day.
- **Filtering**: Filter reports by date to investigate historical backup performance.
- **Detailed Logs**: View lists of failed hosts for immediate remediation.
- **Visual Indicators**: Color-coded status (e.g., failed counts are highlighted) for better visibility.

## Requirements
To run this module, ensure the following backend dependencies are installed (part of the main project's `requirements.txt`):
- **Python 3.8+**
- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **Pydantic**: Data validation and schema definitions.
- **Oracle Client (cx_Oracle/oracledb)**: If connecting to an Oracle database (implied by existing project structure).

## Database Schemas
The module uses a dedicated table for storing backup summaries.

### Table: `SUMMARY_TABLE_FIREWALL_LOGS_BACKUP_NEW`

| Column Name        | Type          | Description                                      |
| ------------------ | ------------- | ------------------------------------------------ |
| `id`               | Integer       | Primary Key (Sequence: `firewall_backup_id_seq`) |
| `task_date`        | Date          | The date when the backup task was executed.      |
| `task_name`        | String(255)   | Name of the backup task (e.g., Checkpoint Backup)|
| `host_count`       | Integer       | Total number of hosts in the task.               |
| `failed_count`     | Integer       | Number of hosts that failed backup.              |
| `failed_hosts`     | Text (CLOB)   | Comma-separated list or details of failed hosts. |
| `successful_hosts` | Text (CLOB)   | Details or count of successful hosts.            |

**Model Definition**: `backend/app/models/firewall_backup.py`

## API Endpoints
The backend exposes RESTful endpoints under the `/api/v1/firewall` prefix (mounted in `backend/app/api/v1/__init__.py`).

### 1. Get Backup Reports
Retrieves a paginated list of backup reports, optionally filtered by date.

- **URL**: `GET /api/v1/firewall/reports`
- **Query Parameters**:
    - `skip` (int, default=0): Number of records to skip.
    - `limit` (int, default=100): Max records to return.
    - `task_date` (date, optional): Filter by specific date (YYYY-MM-DD).
- **Response**: List of `FirewallBackup` objects.

### 2. Get Backup Summary
Retrieves aggregated statistics for the **current day**.

- **URL**: `GET /api/v1/firewall/summary`
- **Response**: `BackupSummary` object.
    ```json
    {
      "total_devices": 150,
      "success_count": 145,
      "failed_count": 5
    }
    ```

**Router Definition**: `backend/app/api/v1/endpoints/firewall_backup.py`

## Features
- **Data Seeding Script**: A script is available to populate the database with dummy data for testing purposes.
- **Frontend Integration**: Angular components are designed to consume these APIs and display data in a tabular format with a summary cards section.
- **Resilience**: The backend handles potential null values in DB stats using `coalesce` (or Python-side handling) to ensure the summary endpoint always returns valid numbers.

## Execution & Usage

### 1. Database Setup
Ensure your database is running and accessible. The application is configured to connect to the database defined in `app.core.database`.

### 2. Seeding Data
To test the dashboard with sample data, run the seeding script. This will generate entries for the past 10 days with random success/failure rates.

```bash
# Navigate to the backend directory
cd backend

# Run the seed script (ensure your python environment is active)
python scripts/seed_firewall_backups.py
```

### 3. Running the Backend
Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```
The APIs will be available at `http://localhost:8000`.

## Configuration
Configuration is primarily handled through environment variables (e.g., `.env`) used by the main application for database connection strings. No specific extra configuration is needed for this module other than ensuring the `SUMMARY_TABLE_FIREWALL_LOGS_BACKUP_NEW` table exists (which `Base.metadata.create_all` typically handles, or the seed script checks).

## Troubleshooting

### Issue: "Database session not available" during seeding
- **Cause**: The script cannot connect to the database.
- **Fix**: Check your `.env` file for correct database credentials (host, port, service name, user, password). Ensure the VPN or network connection to the DB is active.

### Issue: Summary shows 0 for today
- **Cause**: No data exists for the current date (`date.today()`).
- **Fix**: Run the seed script again (it populates data for "today" and past days) or wait for the actual ETL process to populate the table.

### Issue: API returns 500 Internal Server Error
- **Cause**: likely a DB query issue or schema mismatch.
- **Fix**: Check the console logs for Python tracebacks. Verify that the table structure in the DB matches the SQLAlchemy model in `backend/app/models/firewall_backup.py`.
