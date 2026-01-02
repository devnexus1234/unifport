# Capacity Report Catalogue - Documentation

## Table of Contents

1. [Overview](#overview)
2. [Functionalities](#functionalities)
3. [Requirements](#requirements)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Frontend Features](#frontend-features)
7. [Execution & Usage](#execution--usage)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Capacity Report Catalogue is a comprehensive module within the Unified Management Portal that enables organizations to monitor, analyze, and manage IT infrastructure capacity metrics. It provides real-time insights into CPU, memory, and connection utilization across different regions, zones, and devices.

### Key Features

- **Capacity Data Management**: Upload and process Excel files containing capacity metrics
- **Dashboard Visualization**: Interactive dashboard with zone-wise and device-wise capacity summaries
- **Excel Export**: Generate detailed and summary reports in Excel format
- **Device & Zone Management**: CRUD operations for devices and zones
- **Categorized Alerts**: Automatic categorization of devices into Green/Yellow/Red based on threshold values
- **Production Hours Filtering**: Separate analysis for production and non-production hours

---

## Functionalities

### 1. **Capacity Data Upload**

- Upload two Excel files:
  - **Raw Data File**: Contains device capacity metrics (CPU, memory, peak values, alert durations)
  - **Connection Count File**: Contains connection count metrics per device
- Automatic data processing and storage in the database
- Date range filtering for capacity alerts
- Support for parsing complex date-time strings with peak values

### 2. **Interactive Dashboard**

- **Region-based View**: Filter by region (XYZ, ORM-XYZ, DRM, ORM-DRM)
- **Production Hours Toggle**: Switch between production and non-production hours analysis
- **Zone Summary Table**: Displays aggregated metrics per zone:
  - Total device count
  - CPU alerts (Green/Yellow/Red)
  - Memory alerts (Green/Yellow/Red)
- **Device Details**: Expandable zone sections showing individual device metrics:
  - CPU peak percentage
  - CPU peak count (number of alerts)
  - CPU peak duration (minutes)
  - Memory peak percentage
  - Memory peak count
  - Memory peak duration

### 3. **Excel Export**

#### a. **Device Details Export** (`/export`)

- Exports all device capacity data organized by region
- Separate sheets for each region (XYZ, ORM-XYZ, DRM, ORM-DRM)
- Columns include:
  - Zone Name
  - Device Name
  - Mean CPU
  - Peak CPU
  - Mean Memory
  - Peak Memory
  - Mean Connection
  - Peak Connection

#### b. **Summary Export** (`/export-summary`)

- Zone-wise aggregated summary
- Separate sheets for each region and production/non-production hours
- Columns include:
  - Zone Name
  - Total Device Count
  - CPU Green (normal)
  - Memory Green (normal)
  - CPU Yellow (warning)
  - Memory Yellow (warning)
  - CPU Red (critical)
  - Memory Red (critical)

### 4. **Device Management**

- **Add Device**: Add a new device to a specific zone
- **Edit Device**: Update device name or move device to a different zone
- **Delete Device**: Remove device from a zone
- Validation to prevent duplicate device-zone mappings

### 5. **Zone Management**

- **Add Zone**: Create a new zone under a region
- **Edit Zone**: Update zone name within a region
- **Delete Zone**: Remove a zone and its device mappings
- Hierarchical structure: Region → Zone → Device

### 6. **Alert Categorization**

Devices are automatically categorized based on threshold values:

| Category   | CPU Peak | Memory Peak | Description      |
| ---------- | -------- | ----------- | ---------------- |
| **Green**  | < 61%    | < 61%       | Normal operation |
| **Yellow** | 61-70%   | 61-70%      | Warning level    |
| **Red**    | > 70%    | > 70%       | Critical level   |

---

## Requirements

### Backend Dependencies

#### Python Packages

```txt
fastapi>=0.104.0
sqlalchemy>=2.0.0
pandas==2.2.2
openpyxl>=3.1.0
cx_Oracle>=8.3.0
python-multipart>=0.0.6
```

#### Database

- **Oracle Database** (version 12c or higher)
- Required tables:
  - `capacity_values`
  - `zone_device_mapping`
  - `region_zone_mapping`
- Required sequences:
  - `capacity_values_seq`
  - `zone_device_mapping_seq`
  - `region_zone_mapping_seq`

#### Environment Variables

```env
DATABASE_URL=oracle+cx_oracle://username:password@host:port/service_name
```

### Frontend Dependencies

#### Angular Packages

```json
{
  "@angular/core": "^15.0.0",
  "@angular/material": "^15.0.0",
  "@angular/forms": "^15.0.0",
  "@angular/common": "^15.0.0"
}
```

### System Requirements

- **Backend**: Python 3.9+
- **Frontend**: Node.js 16+, Angular 15+
- **Database**: Oracle Database 12c+
- **Browser**: Modern browsers (Chrome, Firefox, Edge, Safari)

---

## Database Schema

### 1. `capacity_values` Table

Stores device capacity metrics.

| Column                  | Type         | Description                      |
| ----------------------- | ------------ | -------------------------------- |
| `id`                    | INTEGER      | Primary key (auto-increment)     |
| `device_name`           | VARCHAR(255) | Device identifier                |
| `mean_cpu`              | FLOAT        | Average CPU utilization          |
| `peak_cpu`              | FLOAT        | Peak CPU utilization             |
| `mean_memory`           | FLOAT        | Average memory utilization       |
| `peak_memory`           | FLOAT        | Peak memory utilization          |
| `mean_connection`       | FLOAT        | Average connection count         |
| `peak_connection`       | FLOAT        | Peak connection count            |
| `cpu_date`              | VARCHAR(255) | Date of CPU peak alert           |
| `cpu_time`              | VARCHAR(255) | Time of CPU peak alert           |
| `memory_date`           | VARCHAR(255) | Date of memory peak alert        |
| `memory_time`           | VARCHAR(255) | Time of memory peak alert        |
| `cpu_alert_duration`    | FLOAT        | CPU alert duration in minutes    |
| `memory_alert_duration` | FLOAT        | Memory alert duration in minutes |
| `ntimes_cpu`            | INTEGER      | Number of CPU alerts             |
| `ntimes_memory`         | INTEGER      | Number of memory alerts          |

### 2. `zone_device_mapping` Table

Maps devices to zones.

| Column        | Type         | Description                  |
| ------------- | ------------ | ---------------------------- |
| `id`          | INTEGER      | Primary key (auto-increment) |
| `zone_name`   | VARCHAR(255) | Zone identifier              |
| `device_name` | VARCHAR(255) | Device identifier            |

### 3. `region_zone_mapping` Table

Maps zones to regions.

| Column        | Type         | Description                  |
| ------------- | ------------ | ---------------------------- |
| `id`          | INTEGER      | Primary key (auto-increment) |
| `region_name` | VARCHAR(100) | Region identifier            |
| `zone_name`   | VARCHAR(255) | Zone identifier              |

### Database Sequences

Ensure the following sequences exist:

```sql
CREATE SEQUENCE capacity_values_seq START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE zone_device_mapping_seq START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE region_zone_mapping_seq START WITH 1 INCREMENT BY 1 NOCACHE;
```

---

## API Endpoints

### Base URL

```
/api/v1/capacity-report
```

### Authentication

All endpoints require authentication via JWT token (except where noted).

### Endpoints

#### 1. **Upload Capacity Files**

```http
POST /upload
Content-Type: multipart/form-data
```

**Request Body:**

- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `raw_data_file` (file, required): Excel file with capacity data
- `connection_count_file` (file, required): Excel file with connection data

**Response:**

```json
{
  "message": "Capacity report processed successfully.",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "raw_data_filename": "raw_data.xlsx",
  "connection_count_filename": "connections.xlsx"
}
```

#### 2. **Export Device Details**

```http
GET /export
```

**Response:** Excel file (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

#### 3. **Export Summary**

```http
GET /export-summary
```

**Query Parameters:**

- `start_date` (optional): Filter start date (DD-MMM-YYYY format)
- `end_date` (optional): Filter end date (DD-MMM-YYYY format)

**Response:** Excel file with summary sheets

#### 4. **Get Dashboard Data**

```http
GET /dashboard
```

**Query Parameters:**

- `region` (required): Region name (XYZ, ORM-XYZ, DRM, ORM-DRM)
- `production_hours` (required): Boolean (true/false)
- `zone_name` (optional): Filter by specific zone

**Response:**

```json
{
  "region": "XYZ",
  "production_hours": true,
  "zone_summary": [
    {
      "zone_name": "XYZ INTERNAL",
      "total_device_count": 10,
      "cpu_normal": 5,
      "cpu_warning": 3,
      "cpu_critical": 2,
      "memory_normal": 6,
      "memory_warning": 2,
      "memory_critical": 2
    }
  ],
  "device_details": [
    {
      "device_name": "DEVICE001",
      "cpu_peak_percent": 85.5,
      "cpu_peak_count": 3,
      "cpu_peak_duration_min": 120.5,
      "memory_peak_percent": 72.3,
      "memory_peak_count": 1,
      "memory_peak_duration_min": 45.0
    }
  ]
}
```

#### 5. **Get Zones**

```http
GET /zones
```

**Response:**

```json
{
  "zones": [
    {
      "zone_name": "XYZ INTERNAL",
      "region_name": "XYZ"
    }
  ]
}
```

#### 6. **Get Devices**

```http
GET /devices
```

**Response:**

```json
{
  "devices": ["DEVICE001", "DEVICE002", "DEVICE003"]
}
```

#### 7. **Get Regions**

```http
GET /regions
```

**Response:**

```json
{
  "regions": ["XYZ", "ORM-XYZ", "DRM", "ORM-DRM"]
}
```

#### 8. **Get Zone-Device Mappings**

```http
GET /zone-device-mappings
```

**Response:**

```json
{
  "mappings": [
    {
      "zone_name": "XYZ INTERNAL",
      "device_name": "DEVICE001"
    }
  ]
}
```

#### 9. **Add Device to Zone**

```http
POST /device-zone-mapping/add
```

**Request Body:**

```json
{
  "zone_name": "XYZ INTERNAL",
  "device_name": "DEVICE001"
}
```

#### 10. **Update Device-Zone Mapping**

```http
PUT /device-zone-mapping/update
```

**Query Parameters:**

- `old_zone_name` (required)
- `old_device_name` (required)
- `new_zone_name` (optional)
- `new_device_name` (optional)

#### 11. **Delete Device-Zone Mapping**

```http
DELETE /device-zone-mapping/delete
```

**Query Parameters:**

- `zone_name` (required)
- `device_name` (required)

#### 12. **Add Zone to Region**

```http
POST /zone-region-mapping/add
```

**Request Body:**

```json
{
  "region_name": "XYZ",
  "zone_name": "XYZ INTERNAL"
}
```

#### 13. **Update Zone-Region Mapping**

```http
PUT /zone-region-mapping/update
```

**Request Body:**

```json
{
  "region_name": "XYZ",
  "zone_name": "XYZ INTERNAL",
  "new_zone_name": "XYZ INTERNAL UPDATED"
}
```

#### 14. **Delete Zone-Region Mapping**

```http
DELETE /zone-region-mapping/delete
```

**Query Parameters:**

- `zone_name` (required)

---

## Frontend Features

### 1. **Capacity Report Upload Form**

- Date range picker for start and end dates
- File upload for raw data and connection count files
- Form validation and error handling
- Success/error notifications

### 2. **Dashboard View**

- **Region Selector**: Dropdown to select region
- **Production Hours Toggle**: Switch between production/non-production hours
- **Zone Summary Table**: Expandable rows showing device details
- **Real-time Data**: Automatic refresh on filter changes
- **Responsive Design**: Works on desktop and tablet devices

### 3. **Device Management Panel**

- **Action Selector**: Choose between ADD, EDIT, DELETE
- **Zone Dropdown**: Select zone (populated from database)
- **Device Input/Dropdown**:
  - Text input for ADD operation
  - Dropdown for EDIT/DELETE operations (filtered by selected zone)
- **New Device Name**: Required field for EDIT operation
- **Form Validation**: Ensures required fields are filled

### 4. **Zone Management Panel**

- **Action Selector**: Choose between ADD, EDIT, DELETE
- **Region Dropdown**: Select region (populated from database)
- **Zone Input/Dropdown**:
  - Text input for ADD operation
  - Dropdown for EDIT/DELETE operations (filtered by selected region)
- **New Zone Name**: Required field for EDIT operation
- **Form Validation**: Ensures required fields are filled

### 5. **Export Buttons**

- **Export Device Details**: Downloads Excel with all device data
- **Export Summary**: Downloads Excel with zone-wise summaries

---

## Execution & Usage

### Backend Setup

1. **Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

2. **Database Configuration**

   - Update `DATABASE_URL` in environment variables or configuration file
   - Ensure Oracle database is accessible
   - Run database migrations/scripts to create tables and sequences

3. **Run Backend Server**

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (using Docker)
docker-compose up -d backend
```

### Frontend Setup

1. **Install Dependencies**

```bash
cd frontend
npm install
```

2. **Configure API URL**

   - Update `environment.ts` or `environment.prod.ts`:

   ```typescript
   export const environment = {
     apiUrl: "http://localhost:8000/api/v1",
     // ... other config
   };
   ```

3. **Run Frontend Server**

```bash
# Development
ng serve

# Production (using Docker)
docker-compose up -d frontend
```

### Usage Workflow

#### Step 1: Upload Capacity Data

1. Navigate to the Capacity Report page
2. Select start and end dates
3. Upload raw data Excel file
4. Upload connection count Excel file
5. Click "Upload" button
6. Wait for processing confirmation

#### Step 2: View Dashboard

1. Select a region from the dropdown
2. Toggle production hours if needed
3. View zone summary table
4. Click on zone rows to expand and see device details

#### Step 3: Manage Devices

1. Click "Modify Device" button
2. Select action (ADD/EDIT/DELETE)
3. Fill required fields:
   - For ADD: Zone name, Device name (text input)
   - For EDIT: Zone name, Device name (dropdown), New device name
   - For DELETE: Zone name, Device name (dropdown)
4. Submit form

#### Step 4: Manage Zones

1. Click "Modify Zone" button
2. Select action (ADD/EDIT/DELETE)
3. Fill required fields:
   - For ADD: Region name, Zone name (text input)
   - For EDIT: Region name, Zone name (dropdown), New zone name
   - For DELETE: Region name, Zone name (dropdown)
4. Submit form

#### Step 5: Export Reports

1. Click "Export Device Details" to download device-level Excel
2. Click "Export Summary" to download zone-wise summary Excel

---

## Configuration

### Threshold Values

Alert categorization thresholds are defined in the backend code:

```python
# CPU/Memory Peak Thresholds
# Green: < 61% (calculated as total_devices - (red + yellow))
# Yellow: 61-70% (peak_min=61, peak_max=70)
# Red: 71-100% (peak_min=71, peak_max=100)

cpu_red = compute_category(zone, prod_hours, 71, 100, ...)
cpu_yellow = compute_category(zone, prod_hours, 61, 70, ...)
cpu_green = max(total_devices - (cpu_red + cpu_yellow), 0)
```

### Production Hours

Production hours are typically defined as:

- **Production**: 09:00 - 18:00 (Monday-Friday)
- **Non-Production**: All other times

### Excel File Format

#### Raw Data File

- Skip first 3 rows (header information)
- Required columns: I, J, K, L, M, N, O, R, T
- Column mapping:
  - Column I: Device Name
  - Column J: Mean CPU
  - Column K: Peak CPU
  - Column L: ntimes_cpu
  - Column M: Mean Memory
  - Column N: Peak Memory
  - Column O: ntimes_memory
  - Column R: First Peak CPU DateTime
  - Column T: First Peak Memory DateTime

#### Connection Count File

- Skip first 5 rows (header information)
- Required columns: C, K, O
- Column mapping:
  - Column C: Entity Name (Device Name)
  - Column K: Mean Connection
  - Column O: Peak Connection

---

## Troubleshooting

### Common Issues

#### 1. **Upload Fails with "File Format Error"**

- **Solution**: Ensure Excel files follow the exact format specified in Configuration section
- Check that required columns are present
- Verify skip rows count matches your file structure

#### 2. **Dashboard Shows No Data**

- **Solution**:
  - Verify data was uploaded successfully
  - Check database connection
  - Ensure zone-device mappings exist
  - Verify region name matches exactly (case-sensitive)

#### 3. **Device/Zone Not Appearing in Dropdown**

- **Solution**:
  - Refresh the page to reload data from database
  - Check if device/zone exists in database
  - Verify zone-device or region-zone mappings are correct

#### 4. **Database Sequence Error (ORA-02289)**

- **Solution**: Run the sequence creation script:
  ```bash
  python backend/scripts/ensure_sequences.py
  ```

#### 5. **CORS Errors in Browser**

- **Solution**:
  - Verify backend CORS configuration allows frontend origin
  - Check that API URL in frontend environment matches backend URL

#### 6. **Excel Export Fails**

- **Solution**:
  - Check browser download permissions
  - Verify user has read access to capacity data
  - Check backend logs for specific error messages

### Debugging

#### Backend Logs

```bash
# View backend logs
docker-compose logs -f backend

# Or if running directly
# Logs are output to console with logger
```

#### Frontend Console

- Open browser Developer Tools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for API request/response details

#### Database Queries

```sql
-- Check capacity values
SELECT * FROM capacity_values WHERE device_name = 'DEVICE001';

-- Check zone-device mappings
SELECT * FROM zone_device_mapping WHERE zone_name = 'XYZ INTERNAL';

-- Check region-zone mappings
SELECT * FROM region_zone_mapping WHERE region_name = 'XYZ';
```

---

## Additional Notes

### Current Limitations

- Excel file processing is currently disabled (commented out) until files are available
- Date filtering for summary export is optional and may not be fully implemented
- Production hours logic may need customization based on organization requirements

### Future Enhancements

- Real-time capacity monitoring
- Email alerts for critical capacity thresholds
- Historical trend analysis
- Custom threshold configuration per zone/device
- API rate limiting and caching
- Bulk device/zone import via CSV

### Support

For issues or questions, contact the development team or refer to the main project documentation.

---

**Last Updated**: January 2025  
**Version**: 1.0.0
