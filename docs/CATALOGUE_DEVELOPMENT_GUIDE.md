# Catalogue Development Guide

This guide explains how to develop, test, and deploy a new catalogue in the Unified Portal system.

## Table of Contents

1. [Overview](#overview)
2. [Catalogue Structure](#catalogue-structure)
3. [Development Workflow](#development-workflow)
4. [Testing in Development](#testing-in-development)
5. [Enabling for Specific Users](#enabling-for-specific-users)
6. [Releasing to All Users](#releasing-to-all-users)
7. [Best Practices](#best-practices)

---

## Overview

A **catalogue** is a feature module in the Unified Portal that provides specific functionality to users. Catalogues are:

- **Organized by Menus**: Each catalogue belongs to a menu (e.g., "Storage", "Network", "Security")
- **Permission-Controlled**: Access is managed via Role-Based Access Control (RBAC)
- **Configurable**: Can be enabled/disabled without code changes
- **Route-Based**: Each catalogue has a frontend route and optional API endpoint

### Key Concepts

- **`is_enabled`**: Controls whether the catalogue is visible to users (default: `false`)
- **`is_active`**: Soft delete flag (default: `true`)
- **`menu_id`**: Required - links catalogue to a menu
- **`frontend_route`**: Frontend route path (e.g., `/storage/vmware`)
- **`api_endpoint`**: Optional backend API endpoint
- **Permissions**: Can be set at menu-level (all catalogues) or catalogue-level (specific)

---

## Catalogue Structure

### Database Model

```python
Catalogue:
  - id: int (primary key)
  - name: str (unique, required)
  - description: str (optional)
  - menu_id: int (required - links to Menu)
  - category_id: int (optional - for backward compatibility)
  - api_endpoint: str (optional - e.g., "/api/v1/storage/vmware")
  - frontend_route: str (optional - e.g., "/storage/vmware")
  - icon: str (optional - Material icon name)
  - is_enabled: bool (default: False) - Controls visibility
  - is_active: bool (default: True) - Soft delete flag
  - display_order: int (default: 0) - Sorting order
  - config: JSON (optional) - Additional configuration
```

### Required Fields for New Catalogue

1. **name**: Unique catalogue name
2. **menu_id**: ID of the menu this catalogue belongs to
3. **frontend_route**: Route path in the frontend application
4. **is_enabled**: Set to `false` initially (enable after testing)

---

## Development Workflow

### Step 1: Create the Catalogue Record

#### Option A: Via Admin UI

1. Log in as an admin user
2. Navigate to **Admin** → **Catalogues**
3. Click **Create New Catalogue**
4. Fill in the required fields:
   - **Name**: e.g., "VMware Storage"
   - **Menu**: Select the appropriate menu
   - **Frontend Route**: e.g., `/storage/vmware`
   - **API Endpoint**: e.g., `/api/v1/storage/vmware` (if needed)
   - **Icon**: e.g., `storage` (Material icon name)
   - **Description**: Brief description of the catalogue
   - **Is Enabled**: ❌ **Leave unchecked** (for development)
   - **Display Order**: Set ordering (lower numbers appear first)

#### Option B: Via API

```bash
POST /api/v1/admin/catalogues
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "VMware Storage",
  "description": "VMware storage management catalogue",
  "menu_id": 1,
  "frontend_route": "/storage/vmware",
  "api_endpoint": "/api/v1/storage/vmware",
  "icon": "storage",
  "display_order": 10,
  "is_enabled": false,
  "is_active": true,
  "config": {
    "version": "1.0",
    "features": ["create", "read", "update"]
  }
}
```

### Step 2: Implement Frontend Component

Create the frontend component for your catalogue:

```typescript
// frontend/src/app/components/catalogues/vmware-storage/vmware-storage.component.ts
import { Component, OnInit } from '@angular/core';
import { CatalogueService } from '../../../services/catalogue.service';

@Component({
  selector: 'app-vmware-storage',
  templateUrl: './vmware-storage.component.html',
  styleUrls: ['./vmware-storage.component.scss']
})
export class VMwareStorageComponent implements OnInit {
  constructor(private catalogueService: CatalogueService) {}

  ngOnInit() {
    // Initialize your catalogue component
  }
}
```

### Step 3: Add Route Configuration

Add the route to your Angular routing module:

```typescript
// frontend/src/app/app-routing.module.ts
import { VMwareStorageComponent } from './components/catalogues/vmware-storage/vmware-storage.component';

const routes: Routes = [
  // ... existing routes
  {
    path: 'storage/vmware',
    component: VMwareStorageComponent,
    canActivate: [AuthGuard]
  }
];
```

### Step 4: Implement Backend API (if needed)

Create backend endpoints for your catalogue:

```python
# backend/app/api/v1/storage.py
from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/storage", tags=["storage"])

@router.get("/vmware")
async def get_vmware_storage(
    current_user: User = Depends(get_current_active_user)
):
    """Get VMware storage information"""
    return {"message": "VMware storage data"}
```

Register the router in `backend/app/api/v1/__init__.py`:

```python
from app.api.v1 import storage

api_router.include_router(storage.router)
```

---

## Testing in Development

### Scenario: Catalogue Enabled but Not Fully Implemented

When a catalogue is enabled in the environment but the implementation is incomplete, you can test it safely:

#### Step 1: Enable Catalogue for Development Only

**Method 1: Enable for Specific Test User**

1. Create a test user or use your development account
2. Assign a role that has access to the catalogue's menu
3. Enable the catalogue (`is_enabled = true`)
4. Only users with the assigned role will see it

**Method 2: Enable with Limited Permissions**

1. Enable the catalogue (`is_enabled = true`)
2. Create a test role specifically for this catalogue
3. Assign catalogue-level permissions to the test role
4. Assign the test role only to your development account

#### Step 2: Test the Catalogue

1. **Access the Catalogue**:
   - Log in with your test account
   - Navigate to the menu that contains your catalogue
   - Verify the catalogue appears in the list

2. **Test Frontend Route**:
   - Navigate directly to the route: `http://localhost:4200/storage/vmware`
   - Verify the component loads correctly
   - Test all UI interactions

3. **Test API Endpoints** (if applicable):
   ```bash
   curl -X GET http://localhost:8000/api/v1/storage/vmware \
     -H "Authorization: Bearer <your_token>"
   ```

4. **Test Error Handling**:
   - Test with invalid data
   - Test with missing permissions
   - Test with network errors

#### Step 3: Monitor Logs

Check backend logs for any errors:

```bash
# Backend logs will show API calls in JSON format
# Look for entries with your catalogue's API endpoint
```

---

## Enabling for Specific Users (Development/Testing)

### Method 1: Role-Based Access (Recommended)

This method allows you to enable the catalogue for specific users without affecting others.

#### Step 1: Create a Test Role

```bash
POST /api/v1/admin/roles
Authorization: Bearer <admin_token>

{
  "name": "VMware Storage Tester",
  "description": "Test role for VMware Storage catalogue",
  "is_active": true
}
```

#### Step 2: Assign Catalogue Permission to Role

```bash
POST /api/v1/admin/roles/{role_id}/catalogue-permissions
Authorization: Bearer <admin_token>

{
  "catalogue_id": <catalogue_id>,
  "permission_type": "read"  # or "write", "admin"
}
```

#### Step 3: Assign Role to Test Users

```bash
POST /api/v1/admin/users/{user_id}/roles
Authorization: Bearer <admin_token>

{
  "role_id": <test_role_id>
}
```

#### Step 4: Enable the Catalogue

```bash
PUT /api/v1/admin/catalogues/{catalogue_id}
Authorization: Bearer <admin_token>

{
  "is_enabled": true
}
```

**Result**: Only users with the "VMware Storage Tester" role will see and access the catalogue.

### Method 2: User-Specific Permissions

For testing with a single user:

1. Enable the catalogue (`is_enabled = true`)
2. Create a user-specific permission (via database or admin UI)
3. Only that specific user will have access

### Method 3: Menu-Level Access

If you want all users with menu access to see the catalogue:

1. Enable the catalogue (`is_enabled = true`)
2. Ensure users have menu-level permissions
3. All users with access to the menu will see the catalogue

**⚠️ Warning**: This method exposes the catalogue to all users with menu access. Use only if you want broad testing.

---

## Releasing to All Users

Once development and testing are complete, follow these steps to release the catalogue to all users:

### Step 1: Final Testing Checklist

- [ ] All features are implemented and tested
- [ ] Error handling is robust
- [ ] Performance is acceptable
- [ ] Security review completed
- [ ] Documentation is updated
- [ ] No critical bugs remain

### Step 2: Enable for Production

#### Option A: Via Admin UI

1. Log in as admin
2. Navigate to **Admin** → **Catalogues**
3. Find your catalogue
4. Click **Edit**
5. Check **Is Enabled**
6. Save changes

#### Option B: Via API

```bash
PUT /api/v1/admin/catalogues/{catalogue_id}
Authorization: Bearer <admin_token>

{
  "is_enabled": true
}
```

### Step 3: Configure Permissions

#### Option A: Menu-Level Access (All Users with Menu Access)

If the catalogue should be available to all users who have access to the menu:

1. Ensure users have menu-level roles/permissions
2. No additional catalogue-level permissions needed
3. The catalogue will automatically appear for all users with menu access

#### Option B: Catalogue-Level Access (Specific Roles)

If you want to restrict access to specific roles:

1. Assign catalogue permissions to the appropriate roles:
   ```bash
   POST /api/v1/admin/roles/{role_id}/catalogue-permissions
   {
     "catalogue_id": <catalogue_id>,
     "permission_type": "read"  # or "write", "admin"
   }
   ```

2. Users with these roles will see the catalogue
3. Users without these roles won't see it (even if they have menu access)

### Step 4: Monitor After Release

1. **Check Logs**: Monitor backend logs for errors
2. **User Feedback**: Collect feedback from early users
3. **Performance**: Monitor API response times
4. **Error Rates**: Watch for increased error rates

### Step 5: Rollback Plan (if needed)

If issues arise, you can quickly disable the catalogue:

```bash
PUT /api/v1/admin/catalogues/{catalogue_id}
{
  "is_enabled": false
}
```

This will hide the catalogue from all users immediately without code changes.

---

## Best Practices

### Development

1. **Always Start with `is_enabled = false`**: Create catalogues in disabled state
2. **Use Descriptive Names**: Clear, concise catalogue names
3. **Set Display Order**: Organize catalogues logically
4. **Add Icons**: Use Material icons for better UX
5. **Document Routes**: Keep frontend routes consistent and documented

### Testing

1. **Test with Limited Users First**: Use role-based access for initial testing
2. **Test Error Scenarios**: Handle edge cases gracefully
3. **Monitor Logs**: Check logs during testing
4. **Test Permissions**: Verify RBAC works correctly

### Security

1. **Always Check Permissions**: Verify user has access before showing data
2. **Validate Input**: Sanitize all user inputs
3. **Use RBAC**: Leverage the built-in permission system
4. **Log Access**: Important operations should be logged

### Deployment

1. **Gradual Rollout**: Enable for test users first, then expand
2. **Monitor Closely**: Watch for issues after enabling
3. **Have Rollback Plan**: Know how to disable quickly
4. **Communicate Changes**: Inform users about new features

### Configuration

1. **Use Config Field**: Store catalogue-specific settings in the `config` JSON field
2. **Environment-Specific**: Different configs for dev/staging/prod
3. **Version Control**: Track config changes

---

## Common Scenarios

### Scenario 1: Testing a Catalogue That's Not Fully Implemented

**Problem**: Catalogue is enabled in environment but implementation is incomplete.

**Solution**:
1. Keep `is_enabled = false` in database
2. Enable only for your test user via role-based permissions
3. Test the implemented features
4. Disable when done testing

### Scenario 2: Enabling for Development Team Only

**Solution**:
1. Create a "Development Team" role
2. Assign catalogue permission to this role
3. Assign role to development team members
4. Enable catalogue (`is_enabled = true`)
5. Only development team will see it

### Scenario 3: Gradual Rollout to Users

**Solution**:
1. Enable catalogue (`is_enabled = true`)
2. Initially assign permissions only to a pilot group
3. Monitor feedback and fix issues
4. Gradually expand permissions to more roles
5. Finally, enable for all users with menu access

### Scenario 4: Disabling a Catalogue Temporarily

**Solution**:
```bash
PUT /api/v1/admin/catalogues/{catalogue_id}
{
  "is_enabled": false
}
```

This hides it from all users immediately. Re-enable when ready.

---

## API Reference

### Create Catalogue

```bash
POST /api/v1/admin/catalogues
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Catalogue Name",
  "description": "Description",
  "menu_id": 1,
  "frontend_route": "/route/path",
  "api_endpoint": "/api/v1/endpoint",
  "icon": "icon_name",
  "display_order": 10,
  "is_enabled": false,
  "config": {}
}
```

### Update Catalogue

```bash
PUT /api/v1/admin/catalogues/{catalogue_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "is_enabled": true  # Enable the catalogue
}
```

### Assign Catalogue Permission to Role

```bash
POST /api/v1/admin/roles/{role_id}/catalogue-permissions
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "catalogue_id": 1,
  "permission_type": "read"  # "read", "write", or "admin"
}
```

### Get All Catalogues (Admin)

```bash
GET /api/v1/admin/catalogues
Authorization: Bearer <admin_token>
```

### Get User-Accessible Catalogues

```bash
GET /api/v1/catalogues
Authorization: Bearer <user_token>
```

Returns only catalogues where `is_enabled = true` and user has permissions.

---

## Troubleshooting

### Catalogue Not Appearing

1. **Check `is_enabled`**: Must be `true`
2. **Check `is_active`**: Must be `true`
3. **Check Permissions**: User must have menu or catalogue-level access
4. **Check Menu**: Menu must be active and user must have access
5. **Check Frontend Route**: Route must be registered in Angular routing

### Permission Denied Errors

1. **Verify Role Assignment**: User must have appropriate role
2. **Check Catalogue Permissions**: Role must have catalogue permission
3. **Check Menu Permissions**: User must have menu-level access (if no catalogue permission)
4. **Verify Admin Status**: Admin users have all permissions

### Frontend Route Not Working

1. **Check Route Registration**: Route must be in `app-routing.module.ts`
2. **Check Component**: Component must exist and be properly imported
3. **Check Auth Guard**: Route may require authentication
4. **Check Browser Console**: Look for JavaScript errors

---

## Summary

The catalogue system provides a flexible way to develop, test, and deploy new features:

1. **Development**: Create catalogue with `is_enabled = false`
2. **Testing**: Enable for specific users via role-based permissions
3. **Release**: Enable for all users with appropriate permissions
4. **Rollback**: Disable instantly if needed

Key points to remember:
- `is_enabled` controls visibility
- Permissions can be menu-level or catalogue-level
- Catalogue-level permissions take precedence
- Admin users have access to all catalogues
- Changes take effect immediately (no code deployment needed)

For questions or issues, contact the development team or refer to the main [CODE_WALKTHROUGH.md](./CODE_WALKTHROUGH.md) documentation.
