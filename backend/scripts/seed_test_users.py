"""
Script to seed database with test users for RBAC testing.
This script:
1. Truncates old seed data (users, roles, permissions)
2. Creates test users with specific access patterns
3. Sets up proper menu and catalogue permissions

Test users:
- user1: Admin with all access
- user2: Only Storage access (all Storage catalogues)
- user3: Storage and Firewall access (all catalogues in both)
- user4: Backup with only "Backup Configuration" catalogue access

Run this after seeding menus and catalogues (seed_menus.py).
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.catalogue import Catalogue
from app.models.menu import Menu
from app.models.rbac import (
    Role, UserRole, MenuPermission, CatalogueRolePermission,
    CataloguePermission
)

def verify_permissions(db, users, menus, catalogues):
    """Verify that users have correct permissions"""
    def check_menu_perm(user, menu_id):
        """Check if user has menu permission"""
        from app.utils.rbac import is_admin_user
        if is_admin_user(user, db):
            return True
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        role_ids = [ur.role_id for ur in user_roles]
        if not role_ids:
            return False
        menu_perm = db.query(MenuPermission).filter(
            MenuPermission.menu_id == menu_id,
            MenuPermission.role_id.in_(role_ids)
        ).first()
        return menu_perm is not None
    
    def check_catalogue_perm(user, catalogue_id):
        """Check if user has catalogue permission"""
        from app.utils.rbac import is_admin_user
        if is_admin_user(user, db):
            return True
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        role_ids = [ur.role_id for ur in user_roles]
        if not role_ids:
            return False
        cat_perm = db.query(CatalogueRolePermission).filter(
            CatalogueRolePermission.catalogue_id == catalogue_id,
            CatalogueRolePermission.role_id.in_(role_ids)
        ).first()
        return cat_perm is not None
    
    for username, user in users.items():
        print(f"\n  {username} ({user.full_name}):")
        
        if user.is_admin:
            print("    ✓ Admin - has access to all menus and catalogues")
            continue
        
        # Check menu access
        accessible_menus = []
        for menu in menus:
            if check_menu_perm(user, menu.id):
                accessible_menus.append(menu.name)
                # Check catalogue access within this menu
                menu_catalogues = [c for c in catalogues if c.menu_id == menu.id]
                accessible_catalogues = []
                for catalogue in menu_catalogues:
                    if check_catalogue_perm(user, catalogue.id):
                        accessible_catalogues.append(catalogue.name)
                print(f"    Menu: {menu.name} - Catalogues: {', '.join(accessible_catalogues) if accessible_catalogues else 'None'}")
        
        if not accessible_menus:
            print("    ⚠ No menu access")

def truncate_seed_data(db):
    """Truncate old seed data"""
    print("Truncating old seed data...")
    
    try:
        # Delete in correct order to respect foreign keys
        db.query(CatalogueRolePermission).delete()
        db.query(MenuPermission).delete()
        db.query(UserRole).delete()
        db.query(CataloguePermission).delete()
        
        # Delete test users (user1, user2, user3, user4) if they exist
        test_usernames = ["user1", "user2", "user3", "user4"]
        for username in test_usernames:
            user = db.query(User).filter(User.username == username).first()
            if user:
                db.delete(user)
        
        # Delete roles (they will be recreated)
        db.query(Role).delete()
        
        db.commit()
        print("✓ Old seed data truncated\n")
    except Exception as e:
        print(f"Error truncating data: {e}")
        db.rollback()
        raise

def seed_test_users():
    """Seed database with test users"""
    db = SessionLocal()
    if db is None:
        print("Warning: Database session not available. Skipping seed.")
        return
    
    try:
        # Truncate old seed data
        truncate_seed_data(db)
        
        # Get menus and catalogues
        menus = db.query(Menu).filter(Menu.is_active == True).all()
        catalogues = db.query(Catalogue).filter(Catalogue.is_active == True).all()
        
        if not menus or not catalogues:
            print("No menus or catalogues found. Please run seed_menus.py first.")
            return
        
        # Create menu map
        menu_map = {menu.name: menu for menu in menus}
        
        # Create catalogue map
        catalogue_map = {cat.name: cat for cat in catalogues}
        
        print(f"Found {len(menus)} menus and {len(catalogues)} catalogues\n")
        
        # Create Admin role (system-wide admin access)
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(
                name="Admin",
                description="System administrator with full access to all menus and catalogues",
                is_active=True
            )
            db.add(admin_role)
            db.flush()
            print(f"Created Admin role")
        
        # Assign Admin role permissions to all menus and catalogues
        for menu in menus:
            # Check if Admin role already has menu permission
            existing_menu_perm = db.query(MenuPermission).filter(
                MenuPermission.role_id == admin_role.id,
                MenuPermission.menu_id == menu.id
            ).first()
            if not existing_menu_perm:
                admin_menu_perm = MenuPermission(
                    role_id=admin_role.id,
                    menu_id=menu.id,
                    permission_type="admin"
                )
                db.add(admin_menu_perm)
            
            # Assign admin permission to all catalogues in this menu
            menu_catalogues = [c for c in catalogues if c.menu_id == menu.id]
            for catalogue in menu_catalogues:
                existing_cat_perm = db.query(CatalogueRolePermission).filter(
                    CatalogueRolePermission.role_id == admin_role.id,
                    CatalogueRolePermission.catalogue_id == catalogue.id
                ).first()
                if not existing_cat_perm:
                    admin_cat_perm = CatalogueRolePermission(
                        role_id=admin_role.id,
                        catalogue_id=catalogue.id,
                        permission_type="admin"
                    )
                    db.add(admin_cat_perm)
        
        # Create Admin role first (system-wide admin access)
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(
                name="Admin",
                description="System administrator with full access to all menus and catalogues",
                is_active=True
            )
            db.add(admin_role)
            db.flush()
            print(f"Created Admin role")
        
        # Assign Admin role permissions to all menus and catalogues
        for menu in menus:
            # Check if Admin role already has menu permission
            existing_menu_perm = db.query(MenuPermission).filter(
                MenuPermission.role_id == admin_role.id,
                MenuPermission.menu_id == menu.id
            ).first()
            if not existing_menu_perm:
                admin_menu_perm = MenuPermission(
                    role_id=admin_role.id,
                    menu_id=menu.id,
                    permission_type="admin"
                )
                db.add(admin_menu_perm)
            
            # Assign admin permission to all catalogues in this menu
            menu_catalogues = [c for c in catalogues if c.menu_id == menu.id]
            for catalogue in menu_catalogues:
                existing_cat_perm = db.query(CatalogueRolePermission).filter(
                    CatalogueRolePermission.role_id == admin_role.id,
                    CatalogueRolePermission.catalogue_id == catalogue.id
                ).first()
                if not existing_cat_perm:
                    admin_cat_perm = CatalogueRolePermission(
                        role_id=admin_role.id,
                        catalogue_id=catalogue.id,
                        permission_type="admin"
                    )
                    db.add(admin_cat_perm)
        
        # Create roles for each menu (for menu-level access)
        menu_roles = {}
        for menu in menus:
            admin_role_name = f"{menu.name} Menu Admin"
            user_role_name = f"{menu.name} Menu User"
            
            # Create admin role
            admin_role = Role(
                name=admin_role_name,
                description=f"Full access to {menu.name} menu and all its catalogues",
                is_active=True
            )
            db.add(admin_role)
            db.flush()
            menu_roles[admin_role_name] = admin_role
            
            # Create user role
            user_role = Role(
                name=user_role_name,
                description=f"Read access to {menu.name} menu and its catalogues",
                is_active=True
            )
            db.add(user_role)
            db.flush()
            menu_roles[user_role_name] = user_role
            
            # Assign menu permissions
            # Menu-level roles get access to ALL catalogues in the menu automatically
            # No need to assign CatalogueRolePermission - the backend logic handles this
            admin_menu_perm = MenuPermission(
                role_id=admin_role.id,
                menu_id=menu.id,
                permission_type="admin"
            )
            db.add(admin_menu_perm)
            
            user_menu_perm = MenuPermission(
                role_id=user_role.id,
                menu_id=menu.id,
                permission_type="read"
            )
            db.add(user_menu_perm)
            
            # Note: We don't assign CatalogueRolePermission for menu-level roles
            # The backend will grant access to all catalogues in the menu based on MenuPermission
        
        # Create specific catalogue roles for granular access
        catalogue_roles = {}
        for catalogue in catalogues:
            role_name = f"{catalogue.name} Access"
            role = Role(
                name=role_name,
                description=f"Access to {catalogue.name} catalogue",
                is_active=True
            )
            db.add(role)
            db.flush()
            catalogue_roles[role_name] = role
            
            # Get the menu for this catalogue
            menu = next((m for m in menus if m.id == catalogue.menu_id), None)
            if menu:
                # Give menu read permission
                menu_perm = MenuPermission(
                    role_id=role.id,
                    menu_id=menu.id,
                    permission_type="read"
                )
                db.add(menu_perm)
            
            # Give catalogue read permission
            cat_perm = CatalogueRolePermission(
                role_id=role.id,
                catalogue_id=catalogue.id,
                permission_type="read"
            )
            db.add(cat_perm)
        
        db.commit()
        print(f"Created {len(menu_roles)} menu roles and {len(catalogue_roles)} catalogue roles\n")
        
        # Create test users
        test_users = [
            {
                "username": "user1",
                "email": "user1@example.com",
                "full_name": "Admin User",
                "is_admin": False,  # Admin via role, not flag
                "is_active": True,
                "roles": ["Admin"]  # Admin role provides full access
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "full_name": "Storage Only User",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Menu Admin"]  # Full access to Storage menu and all its catalogues
            },
            {
                "username": "user3",
                "email": "user3@example.com",
                "full_name": "Storage and Firewall User",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Menu Admin", "Firewall Menu Admin"]  # Full access to both menus
            },
            {
                "username": "user4",
                "email": "user4@example.com",
                "full_name": "Backup Configuration Only User",
                "is_admin": False,
                "is_active": True,
                "roles": ["Backup Configuration Access"]  # Only Backup Configuration catalogue
            }
        ]
        
        created_users = {}
        all_roles = {"Admin": admin_role, **menu_roles, **catalogue_roles}
        
        for user_data in test_users:
            roles_list = user_data.pop("roles")
            
            # Create or update user
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                for key, value in user_data.items():
                    setattr(existing_user, key, value)
                db.flush()
                created_users[user_data["username"]] = existing_user
                print(f"Updated user: {user_data['username']} ({user_data['full_name']})")
            else:
                user = User(**user_data)
                db.add(user)
                db.flush()
                created_users[user_data["username"]] = user
                print(f"Created user: {user_data['username']} ({user_data['full_name']})")
            
            # Assign roles to user
            user = created_users[user_data["username"]]
            for role_name in roles_list:
                if role_name in all_roles:
                    existing_assignment = db.query(UserRole).filter(
                            UserRole.user_id == user.id,
                            UserRole.role_id == all_roles[role_name].id
                        ).first()
                        
                        if not existing_assignment:
                            user_role = UserRole(
                                user_id=user.id,
                                role_id=all_roles[role_name].id,
                                is_dl=False
                            )
                            db.add(user_role)
                            print(f"  Assigned role: {role_name}")
                    else:
                        print(f"  Warning: Role '{role_name}' not found")
        
        db.commit()
        
        print(f"\n✓ Successfully created {len(created_users)} test users!")
        print("\nTest Users Summary:")
        for username, user in created_users.items():
            if user.is_admin:
                print(f"  - {user.full_name} ({username}): ADMIN - All Access")
            else:
                user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
                role_names = [db.query(Role).filter(Role.id == ur.role_id).first().name 
                             for ur in user_roles if db.query(Role).filter(Role.id == ur.role_id).first()]
                print(f"  - {user.full_name} ({username}): {', '.join(role_names)}")
        
        print("\nAccess Summary:")
        print("  user1 (admin): Can see all menus and catalogues")
        print("  user2: Can see only Storage menu with all Storage catalogues")
        print("  user3: Can see Storage and Firewall menus with all their catalogues")
        print("  user4: Can see Backup menu but only Backup Configuration catalogue")
        
        # Verify permissions
        print("\nVerifying permissions...")
        verify_permissions(db, created_users, menus, catalogues)
        
    except Exception as e:
        print(f"Error seeding test users: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_users()
