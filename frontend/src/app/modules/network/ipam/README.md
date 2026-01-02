# IPAM (IP Address Management) Module

## 🎯 Objective
The **IPAM** module provides a centralized interface for managing IP address segments and individual IP allocations. It replaces manual spreadsheets with a structured, queryable database, allowing network engineers to track IP usage, assignments, and availability across different environments, entities, and locations.

## ✨ Features

### 1. Segment Management
*   **Segment Catalogue**: View all network segments (CIDR blocks) in a paginated, filterable list.
*   **Search & Filter**: Quickly find segments by Entity, Environment, Location, or free-text search.
*   **Status Overview**: Immediate visibility into assigned vs. unassigned IPs per segment.

### 2. IP Allocation
*   **Detailed View**: Drill down into specific segments to view individual IP addresses.
*   **Status Tracking**: IPs are categorized as **Assigned**, **Unassigned**, or **Reserved**.
*   **Assignment Workflow**:
    *   Edit IP details via a dedicated dialog.
    *   Assign IPs to specific owners/sources.
    *   Add comments and RITM (Request Item) references for audit trails.

### 3. Visual Cues & UX
*   **Color-Coded Status**: "Assigned" (Red) and "Unassigned" (Green) badges for quick status recognition.
*   **Dark Mode Support**: Fully optimized for dark mode with high-contrast elements.
*   **Responsive Design**: Tables and filters adapt to different screen sizes.

---

## 🏗️ Code Walkthrough (For Developers)

This module follows a `{category}/{catalogue}` structure.

### 1. The Database Layer (Models)
Located in: `backend/app/models/ipam.py`

*   **`IpamSegment`**: Represents a CIDR block (e.g., `192.168.1.0/24`). Contains metadata like location, entity, and environment.
*   **`IpamAllocation`**: Represents individual IPs within a segment. Tracks usage status and assignment details.

### 2. The Backend Logic (API)
Located in: `backend/app/api/v1/network/ipam.py`

*   **Endpoints**: RESTful API endpoints for:
    *   Listing segments with usage stats.
    *   Fetching IPs for a specific segment.
    *   Updating IP allocation details.
*   **Logic**: Handles data retrieval and updates via SQLAlchemy.

### 3. The Frontend (Angular)
Located in: `frontend/src/app/modules/network/ipam/`

*   **`IpamList`**: Displays the table of segments. Handles global filters (Entity, Env, Location) and search.
*   **`IpamDetail`**: Displays the list of IPs for a selected segment. Supports filtering by status and other attributes.
*   **`IpamService`**: Communicates with the backend API at `/api/v1/network/ipam`.

---

## ⚙️ Configuration

No specific environment variables are required for IPAM beyond the standard database connection. The module reuses the core backend configuration.

## 🔌 API Reference (Key Endpoints)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/network/ipam/segments` | List all IP segments with usage counts. |
| `GET` | `/api/v1/network/ipam/segments/{id}/ips` | Get all IP addresses for a specific segment. |
| `PUT` | `/api/v1/network/ipam/segments/{id}/ips/{ip}` | Update status/assignment of a specific IP. |
