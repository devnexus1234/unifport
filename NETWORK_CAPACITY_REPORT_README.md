# Network Capacity Report Catalogue - Documentation

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

The Network Capacity Report Catalogue is a specialized module within the Unified Management Portal designed to monitor and analyze capacity metrics for network infrastructure devices. It provides insights into CPU and memory utilization across different regions and zones.

### Key Features

- **Network Capacity Data Management**: Upload and process network capacity data files
- **Dashboard Visualization**: Interactive dashboard with region-wise and zone-wise capacity summaries
- **Excel Export**: Generate detailed and summary reports
- **Device & Zone Management**: CRUD operations for network devices and zones
- **Categorized Alerts**: Automatic categorization of devices into Green/Yellow/Red based on CPU and Memory thresholds
- **Production Hours Filtering**: Separate analysis for production and non-production hours

---

## Functionalities

### 1. **Network Capacity Data Upload**

- Upload a single Excel file:
  - **Network Data File**: Contains device capacity metrics (CPU, memory, peak values, alert durations)
- Automatic data processing and storage in the database
- Support for parsing complex date-time strings with peak values

### 2. **Interactive Dashboard**

- **Region-based View**: Filter by region (XYZ, ORM-XYZ, DRM, ORM-DRM)
- **Production Hours Toggle**: Switch between production and non-production hours analysis
- **Zone Summary Table**: Displays aggregated metrics per zone:
  - Total device count
  - CPU alerts (Green/Yellow/Red)
  - Memory alerts (Green/Yellow/Red)
- **Device Details**: Expandable zone sections showing individual device metrics:
  - CPU peak percentage, count, and duration
  - Memory peak percentage, count, and duration

### 3. **Excel Export**

#### a. **Device Details Export** (`/export`)

- Exports all network device capacity data organized by region
- Separate sheets for each region
- Columns include: Region, Zone, Device Name, Mean/Peak CPU, Mean/Peak Memory

#### b. **Summary Export** (`/export-summary`)

- Zone-wise aggregated summary
- Separate sheets for each region and production/non-production hours
- Columns include: Zone Name, Total Device Count, CPU/Memory counts by category (Green, Yellow, Red)

### 4. **Device Management**

- **Add Device**: Add a new device to a specific zone
- **Edit Device**: Update device name or move device to a different zone
- **Delete Device**: Remove device from a zone
- Validation to prevent duplicate device-zone mappings

### 5. **Zone Management**

- **Add Zone**: Create a new zone under a region
- **Edit Zone**: Update zone name within a region
- **Delete Zone**: Remove a zone
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

- **FastAPI**, **SQLAlchemy**, **Pandas**, **OpenPyXL**, **cx_Oracle**
- **Database**: Oracle Database (12c+)

### Database Schema

#### 1. `capacity_network_values` Table

Stores network device capacity metrics.

| Column                  | Type         | Description                      |
| ----------------------- | ------------ | -------------------------------- |
| `id`                    | INTEGER      | Primary key                      |
| `device_name`           | VARCHAR(255) | Device identifier                |
| `mean_cpu`              | FLOAT        | Average CPU utilization          |
| `peak_cpu`              | FLOAT        | Peak CPU utilization             |
| `mean_memory`           | FLOAT        | Average memory utilization       |
| `peak_memory`           | FLOAT        | Peak memory utilization          |
| `cpu_date`              | VARCHAR(255) | Date of CPU peak alert           |
| `cpu_time`              | VARCHAR(255) | Time of CPU peak alert           |
| `memory_date`           | VARCHAR(255) | Date of memory peak alert        |
| `memory_time`           | VARCHAR(255) | Time of memory peak alert        |
| `cpu_alert_duration`    | FLOAT        | CPU alert duration (min)         |
| `memory_alert_duration` | FLOAT        | Memory alert duration (min)      |
| `ntimes_cpu`            | INTEGER      | CPU alert count                  |
| `ntimes_memory`         | INTEGER      | Memory alert count               |

#### 2. `zone_device_mapping_network` Table

Maps network devices to zones.

#### 3. `region_zone_mapping_network` Table

Maps zones to regions.

### Database Sequences

- `capacity_network_values_seq`
- `zone_device_mapping_network_seq`
- `region_zone_mapping_network_seq`

---

## API Endpoints

### Base URL

```
/api/v1/capacity-network-report
```

### Endpoints

1.  **POST `/upload`**: Upload `network_data_file`.
2.  **GET `/export`**: Download device details Excel.
3.  **GET `/export-summary`**: Download summary Excel.
4.  **GET `/dashboard`**: Get dashboard data (params: `region`, `production_hours`, optional `zone_name`).
5.  **GET `/zones`**: List all zones.
6.  **GET `/devices`**: List all devices.
7.  **GET `/regions`**: List all regions.
8.  **GET `/zone-device-mappings`**: List mappings.
9.  **POST `/device-zone-mapping/add`**, **PUT `/update`**, **DELETE `/delete`**: Manage device mappings.
10. **POST `/zone-region-mapping/add`**, **PUT `/update`**, **DELETE `/delete`**: Manage zone mappings.

---

## Execution & Usage

Follow the general backend and frontend setup instructions in the main README.

### Usage Workflow

1.  **Upload**: Go to Network Capacity Report, upload the Network Data Excel file.
2.  **Dashboard**: Filter by Region (XYZ, etc.) and toggle Production Hours to view zone stats.
3.  **Drill Down**: Click a zone to view individual device metrics (CPU/Memory peaks, durations).
4.  **Modify**: Use the buttons to Add/Edit/Delete zones and devices as needed.
5.  **Export**: Download the detailed or summary Excel reports.

---

## Configuration

### Excel File Format

- **Network Data File**:
    - Skip first 3 rows.
    - Required columns mapped to: Device Name, Mean/Peak CPU, ntimes CPU, Mean/Peak Memory, ntimes Memory, First Peak Dates.

---

## Troubleshooting

- **Upload Issues**: Ensure the Excel file matches the expected format (header rows, column order).
- **Missing Data**: Verify that `region_zone_mapping_network` and `zone_device_mapping_network` tables are populated.
- **Database Errors**: Check if the tables and sequences exist in the Oracle database.
