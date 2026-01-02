# RBAC (Role-Based Access Control) System Documentation

## Overview

The Unified Management Portal implements a comprehensive Role-Based Access Control (RBAC) system that controls access to:
- **Menus** (Sidenav items like Storage, Backup, Firewall, Linux)
- **Catalogues** (Items under each menu)

Users are assigned roles, and roles are granted permissions to access menus and catalogues. This provides fine-grained access control across the application.

## Architecture

### Database Models

#### 1. Role
Represents a role that can be assigned to users.

**Table**: `roles`
- `id`: Primary key
- `name`: Unique role name (e.g., "Storage Admin", "Backup User")
- `description`: Optional description
- `is_active`: Whether the role is active

#### 2. Menu
Represents sidenav menu items (Storage, Backup, Firewall, Linux, etc.).

**Table**: `menus`
- `id`: Primary key
- `name`: Menu name (e.g., "Storage", "Backup")
- `description`: Optional description
- `icon`: Material icon name
- `display_order`: Order in which menus appear
- `is_active`: Whether the menu is active

#### 3. Catalogue
Represents catalogues/items under each menu.

**Table**: `catalogues`
- `id`: Primary key
- `name`: Catalogue name
- `description`: Optional description
- `menu_id`: Foreign key to `menus` table
- `icon`: Material icon name
- `frontend_route`: Frontend route path
- `api_endpoint`: Backend API endpoint
- `is_enabled`: Whether the catalogue is enabled
- `is_active`: Whether the catalogue is active
- `display_order`: Order in which catalogues appear

#### 4. MenuPermission
Role-based permissions for menus.

**Table**: `menu_permissions`
- `id`: Primary key
- `menu_id`: Foreign key to `menus` table
- `role_id`: Foreign key to `roles` table
- `permission_type`: One of `'read'`, `'write'`, `'admin'`

#### 5. CatalogueRolePermission
Role-based permissions for catalogues.

**Table**: `catalogue_role_permissions`
- `id`: Primary key
- `catalogue_id`: Foreign key to `catalogues` table
- `role_id`: Foreign key to `roles` table
- `permission_type`: One of `'read'`, `'write'`, `'admin'`

#### 6. UserRole
Maps users to roles.

**Table**: `user_role_mapping`
- `id`: Primary key
- `user_id`: Foreign key to `users` table
- `role_id`: Foreign key to `roles` table
- `is_dl`: Whether this is a Distribution List
- `dl_name`: Distribution List name (if `is_dl` is True)

**Note**: User-role assignments can only be done via backend/database directly. There is no API endpoint for assigning roles to users.

## Permission Types

- **read**: User can view/access the resource
- **write**: User can modify the resource
- **admin**: User has full administrative access to the resource

## Access Control Flow

### Menu Access
1. User logs in and requests the menu
2. System checks if user is admin → If yes, show all menus
3. System retrieves all roles assigned to the user
4. For each menu, check if any of the user's roles have a `MenuPermission` for that menu
5. Only show menus where the user has at least `read` permission

### Catalogue Access
1. User requests catalogues for a menu
2. System checks if user is admin → If yes, show all catalogues
3. System retrieves all roles assigned to the user
4. For each catalogue, check:
   - User-specific permissions (`CataloguePermission`)
   - Distribution List permissions (`CataloguePermission` with `dl_name`)
   - Role-based permissions (`CatalogueRolePermission`)
5. Only show catalogues where the user has at least `read` permission

## API Endpoints

### Menu API
- `GET /api/v1/menu` - Get menu structure based on user permissions

### Admin API (Admin Only)

#### Role Management
- `GET /api/v1/admin/roles` - Get all roles
- `GET /api/v1/admin/roles/{role_id}` - Get role with permissions
- `POST /api/v1/admin/roles` - Create new role
- `PUT /api/v1/admin/roles/{role_id}` - Update role
- `DELETE /api/v1/admin/roles/{role_id}` - Delete (deactivate) role

#### Menu Permissions
- `POST /api/v1/admin/roles/{role_id}/menu-permissions` - Assign menu permission to role
- `DELETE /api/v1/admin/roles/{role_id}/menu-permissions/{menu_id}` - Remove menu permission

#### Catalogue Permissions
- `POST /api/v1/admin/roles/{role_id}/catalogue-permissions` - Assign catalogue permission to role
- `DELETE /api/v1/admin/roles/{role_id}/catalogue-permissions/{catalogue_id}` - Remove catalogue permission

#### Reference Data
- `GET /api/v1/admin/menus` - Get all menus (for admin panel)
- `GET /api/v1/admin/catalogues?menu_id={menu_id}` - Get all catalogues (for admin panel)

## Admin Panel

The admin panel provides a UI for:
1. **Creating and managing roles**
   - Create new roles
   - Edit role name and description
   - Delete (deactivate) roles

2. **Assigning menu permissions to roles**
   - Select which menus a role can access
   - Set permission type (read/write/admin) for each menu

3. **Assigning catalogue permissions to roles**
   - Select which catalogues a role can access
   - Set permission type (read/write/admin) for each catalogue
   - Catalogues are grouped by their parent menu

## Assigning Roles to Users

**Important**: User-role assignments can only be done via backend/database directly. There is no API endpoint or UI for this.

### Method 1: Direct Database Insert

```sql
-- Assign a role to a user
INSERT INTO user_role_mapping (user_id, role_id, is_dl, dl_name)
VALUES (
    (SELECT id FROM users WHERE username = 'john.doe'),
    (SELECT id FROM roles WHERE name = 'Storage Admin'),
    false,
    NULL
);
```

### Method 2: Using Python Script

Create a script `assign_role.py`:

```python
from app.core.database import SessionLocal
from app.models.user import User
from app.models.rbac import Role, UserRole

db = SessionLocal()

# Get user and role
user = db.query(User).filter(User.username == 'john.doe').first()
role = db.query(Role).filter(Role.name == 'Storage Admin').first()

# Create user-role mapping
user_role = UserRole(user_id=user.id, role_id=role.id, is_dl=False)
db.add(user_role)
db.commit()
db.close()
```

### Method 3: Using SQLAlchemy in Python Shell

```python
from app.core.database import SessionLocal
from app.models.user import User
from app.models.rbac import Role, UserRole

db = SessionLocal()

user = db.query(User).filter(User.username == 'john.doe').first()
role = db.query(Role).filter(Role.name == 'Storage Admin').first()

if user and role:
    # Check if mapping already exists
    existing = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.role_id == role.id
    ).first()
    
    if not existing:
        user_role = UserRole(user_id=user.id, role_id=role.id, is_dl=False)
        db.add(user_role)
        db.commit()
        print(f"Assigned role '{role.name}' to user '{user.username}'")
    else:
        print("Role already assigned to user")

db.close()
```

## Seed Data

The system includes a seed script that creates:
- Default menus: Storage, Backup, Firewall, Linux
- Sample catalogues for each menu
- Default roles: Admin and User roles for each menu
- Default permissions: Admin roles get full access, User roles get read access

### Running Seed Script

```bash
cd backend
python scripts/seed_menus.py
```

This will create:
- 4 menus (Storage, Backup, Firewall, Linux)
- 8 catalogues (2 per menu)
- 8 roles (Admin and User for each menu)
- Menu permissions for each role
- Catalogue permissions for admin roles

## Default Roles Created by Seed Script

1. **Storage Admin** - Full access to Storage menu and catalogues
2. **Storage User** - Read access to Storage menu and catalogues
3. **Backup Admin** - Full access to Backup menu and catalogues
4. **Backup User** - Read access to Backup menu and catalogues
5. **Firewall Admin** - Full access to Firewall menu and catalogues
6. **Firewall User** - Read access to Firewall menu and catalogues
7. **Linux Admin** - Full access to Linux menu and catalogues
8. **Linux User** - Read access to Linux menu and catalogues

## Best Practices

1. **Role Naming**: Use descriptive names like "Storage Admin", "Backup User", etc.
2. **Permission Types**: 
   - Use `read` for users who only need to view
   - Use `write` for users who need to modify
   - Use `admin` for users who need full control
3. **User-Role Assignment**: Always assign roles via database to maintain security
4. **Role Deactivation**: Instead of deleting roles, set `is_active = false` to preserve history
5. **Testing**: Test permissions after assigning roles to ensure users see the correct menus and catalogues

## Troubleshooting

### User can't see menus
1. Check if user has roles assigned: `SELECT * FROM user_role_mapping WHERE user_id = ?`
2. Check if roles have menu permissions: `SELECT * FROM menu_permissions WHERE role_id IN (?)`
3. Check if menus are active: `SELECT * FROM menus WHERE is_active = true`

### User can't see catalogues
1. Check if user's roles have catalogue permissions: `SELECT * FROM catalogue_role_permissions WHERE role_id IN (?)`
2. Check if catalogues are enabled: `SELECT * FROM catalogues WHERE is_enabled = true AND is_active = true`
3. Check if catalogues belong to menus the user can access

### Admin can't access admin panel
1. Verify user has `is_admin = true` in the `users` table
2. Check if admin guard is working correctly

## Security Considerations

1. **User-Role Assignment**: Only via database to prevent unauthorized role escalation
2. **Admin Access**: Admin users bypass all permission checks
3. **API Security**: All admin endpoints require admin authentication
4. **Permission Checks**: Always verify permissions on both frontend and backend
5. **Role Deactivation**: Deactivated roles don't grant permissions even if assigned to users

## Example Workflow

1. **Create a new role** via Admin Panel:
   - Go to Admin → Roles & Permissions
   - Click "New Role"
   - Enter name: "Storage Manager"
   - Enter description: "Manages storage resources"

2. **Assign menu permissions**:
   - Select the role
   - In "Menu Permissions", check "Storage"
   - Set permission type to "admin"

3. **Assign catalogue permissions**:
   - In "Catalogue Permissions", expand "Storage"
   - Check all storage catalogues
   - Set permission type to "admin" for each

4. **Assign role to user** (via database):
   ```sql
   INSERT INTO user_role_mapping (user_id, role_id, is_dl, dl_name)
   VALUES (
       (SELECT id FROM users WHERE username = 'storage.manager'),
       (SELECT id FROM roles WHERE name = 'Storage Manager'),
       false,
       NULL
   );
   ```

5. **Verify**:
   - User logs in
   - User should see "Storage" menu in sidenav
   - User should see all storage catalogues
   - User should have admin access to storage resources

## Additional Resources

- API Documentation: http://localhost:8000/docs (when backend is running)
- Database Schema: See `backend/app/models/` for model definitions
- Seed Script: `backend/scripts/seed_menus.py`
