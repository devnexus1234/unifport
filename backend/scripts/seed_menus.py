"""
Script to seed database with default menus (Storage, Backup, Firewall, Linux) and sample catalogues.
Run this after initializing the database.
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.menu import Menu
from app.models.catalogue import Catalogue, CatalogueCategory
from app.models.rbac import Role, MenuPermission, CatalogueRolePermission

def seed_menus():
    """Seed database with default menus and catalogues"""
    db = SessionLocal()
    if db is None:
        print("Warning: Database session not available. Skipping seed.")
        return
    
    try:
        # Create default menus
        menus_data = [
            {"name": "Storage", "description": "Storage management and automation", "icon": "storage", "display_order": 1},
            {"name": "Backup", "description": "Backup and recovery management", "icon": "backup_restore", "display_order": 2},
            {"name": "Firewall", "description": "Firewall configuration and management", "icon": "security", "display_order": 3},
            {"name": "Linux", "description": "Linux system management and automation", "icon": "computer", "display_order": 4},
        ]
        
        created_menus = {}
        for menu_data in menus_data:
            existing = db.query(Menu).filter(Menu.name == menu_data["name"]).first()
            if not existing:
                menu = Menu(**menu_data)
                db.add(menu)
                db.flush()  # Get the ID
                created_menus[menu_data["name"]] = menu
                print(f"Created menu: {menu_data['name']}")
            else:
                created_menus[menu_data["name"]] = existing
                print(f"Menu already exists: {menu_data['name']}")
        
        db.commit()
        
        # Get or create a default category for catalogues (for backward compatibility)
        default_category = db.query(CatalogueCategory).filter(CatalogueCategory.name == "Storage").first()
        if not default_category:
            # Create a default category if none exists
            default_category = CatalogueCategory(
                name="Default",
                description="Default category for catalogues",
                icon="folder",
                display_order=0
            )
            db.add(default_category)
            db.flush()
        
        # Create sample catalogues for each menu
        catalogues_data = [
            # Storage catalogues
            {
                "name": "Storage Provisioning",
                "description": "Provision and manage storage resources",
                "menu_id": created_menus["Storage"].id,
                "category_id": default_category.id,  # Provide category_id to avoid NULL constraint
                "icon": "add_circle",
                "frontend_route": "/storage/provisioning",
                "api_endpoint": "/api/v1/storage/provision",
                "display_order": 1,
                "is_enabled": True
            },
            {
                "name": "Storage Monitoring",
                "description": "Monitor storage usage and performance",
                "menu_id": created_menus["Storage"].id,
                "category_id": default_category.id,
                "icon": "monitoring",
                "frontend_route": "/storage/monitoring",
                "api_endpoint": "/api/v1/storage/monitor",
                "display_order": 2,
                "is_enabled": True
            },
            # Backup catalogues
            {
                "name": "Backup Configuration",
                "description": "Configure backup policies and schedules",
                "menu_id": created_menus["Backup"].id,
                "category_id": default_category.id,
                "icon": "settings_backup_restore",
                "frontend_route": "/backup/configuration",
                "api_endpoint": "/api/v1/backup/config",
                "display_order": 1,
                "is_enabled": True
            },
            {
                "name": "Backup Restore",
                "description": "Restore data from backups",
                "menu_id": created_menus["Backup"].id,
                "category_id": default_category.id,
                "icon": "restore",
                "frontend_route": "/backup/restore",
                "api_endpoint": "/api/v1/backup/restore",
                "display_order": 2,
                "is_enabled": True
            },
            # Firewall catalogues
            {
                "name": "Firewall Rules",
                "description": "Manage firewall rules and policies",
                "menu_id": created_menus["Firewall"].id,
                "category_id": default_category.id,
                "icon": "rule",
                "frontend_route": "/firewall/rules",
                "api_endpoint": "/api/v1/firewall/rules",
                "display_order": 1,
                "is_enabled": True
            },
            {
                "name": "Firewall Logs",
                "description": "View and analyze firewall logs",
                "menu_id": created_menus["Firewall"].id,
                "category_id": default_category.id,
                "icon": "description",
                "frontend_route": "/firewall/logs",
                "api_endpoint": "/api/v1/firewall/logs",
                "display_order": 2,
                "is_enabled": True
            },
            # Linux catalogues
            {
                "name": "Linux Server Management",
                "description": "Manage Linux servers and configurations",
                "menu_id": created_menus["Linux"].id,
                "category_id": default_category.id,
                "icon": "dns",
                "frontend_route": "/linux/servers",
                "api_endpoint": "/api/v1/linux/servers",
                "display_order": 1,
                "is_enabled": True
            },
            {
                "name": "Linux Package Management",
                "description": "Manage packages and software on Linux systems",
                "menu_id": created_menus["Linux"].id,
                "category_id": default_category.id,
                "icon": "apps",
                "frontend_route": "/linux/packages",
                "api_endpoint": "/api/v1/linux/packages",
                "display_order": 2,
                "is_enabled": True
            },
        ]
        
        for cat_data in catalogues_data:
            existing = db.query(Catalogue).filter(Catalogue.name == cat_data["name"]).first()
            if not existing:
                catalogue = Catalogue(**cat_data)
                db.add(catalogue)
                print(f"Created catalogue: {cat_data['name']}")
            else:
                print(f"Catalogue already exists: {cat_data['name']}")
        
        db.commit()
        print("\nMenus and catalogues seeded successfully!")
        
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
        else:
            print(f"Admin role already exists")
        
        # Get all menus and catalogues for Admin role permissions
        all_menus = db.query(Menu).all()
        all_catalogues = db.query(Catalogue).all()
        
        # Assign Admin role permissions to all menus
        for menu in all_menus:
            existing = db.query(MenuPermission).filter(
                MenuPermission.role_id == admin_role.id,
                MenuPermission.menu_id == menu.id
            ).first()
            if not existing:
                perm = MenuPermission(
                    role_id=admin_role.id,
                    menu_id=menu.id,
                    permission_type="admin"
                )
                db.add(perm)
                print(f"Assigned admin permission on {menu.name} menu to Admin role")
        
        # Assign Admin role permissions to all catalogues
        for catalogue in all_catalogues:
            existing = db.query(CatalogueRolePermission).filter(
                CatalogueRolePermission.role_id == admin_role.id,
                CatalogueRolePermission.catalogue_id == catalogue.id
            ).first()
            if not existing:
                perm = CatalogueRolePermission(
                    role_id=admin_role.id,
                    catalogue_id=catalogue.id,
                    permission_type="admin"
                )
                db.add(perm)
                print(f"Assigned admin permission on {catalogue.name} catalogue to Admin role")
        
        db.commit()
        
        # Create default roles if they don't exist
        roles_data = [
            {"name": "Storage Admin", "description": "Full access to Storage menu and catalogues"},
            {"name": "Backup Admin", "description": "Full access to Backup menu and catalogues"},
            {"name": "Firewall Admin", "description": "Full access to Firewall menu and catalogues"},
            {"name": "Linux Admin", "description": "Full access to Linux menu and catalogues"},
            {"name": "Storage User", "description": "Read access to Storage menu and catalogues"},
            {"name": "Backup User", "description": "Read access to Backup menu and catalogues"},
            {"name": "Firewall User", "description": "Read access to Firewall menu and catalogues"},
            {"name": "Linux User", "description": "Read access to Linux menu and catalogues"},
        ]
        
        created_roles = {}
        for role_data in roles_data:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                role = Role(**role_data)
                db.add(role)
                db.flush()
                created_roles[role_data["name"]] = role
                print(f"Created role: {role_data['name']}")
            else:
                created_roles[role_data["name"]] = existing
                print(f"Role already exists: {role_data['name']}")
        
        db.commit()
        
        # Assign menu permissions to roles
        menu_role_mappings = [
            ("Storage Admin", "Storage", "admin"),
            ("Storage User", "Storage", "read"),
            ("Backup Admin", "Backup", "admin"),
            ("Backup User", "Backup", "read"),
            ("Firewall Admin", "Firewall", "admin"),
            ("Firewall User", "Firewall", "read"),
            ("Linux Admin", "Linux", "admin"),
            ("Linux User", "Linux", "read"),
        ]
        
        for role_name, menu_name, perm_type in menu_role_mappings:
            if role_name in created_roles and menu_name in created_menus:
                existing = db.query(MenuPermission).filter(
                    MenuPermission.role_id == created_roles[role_name].id,
                    MenuPermission.menu_id == created_menus[menu_name].id
                ).first()
                if not existing:
                    perm = MenuPermission(
                        role_id=created_roles[role_name].id,
                        menu_id=created_menus[menu_name].id,
                        permission_type=perm_type
                    )
                    db.add(perm)
                    print(f"Assigned {perm_type} permission on {menu_name} to {role_name}")
        
        db.commit()
        
        # Assign catalogue permissions to roles (admin roles get all catalogues in their menu)
        for role_name, menu_name in [("Storage Admin", "Storage"), ("Backup Admin", "Backup"), 
                                     ("Firewall Admin", "Firewall"), ("Linux Admin", "Linux")]:
            if role_name in created_roles and menu_name in created_menus:
                menu = created_menus[menu_name]
                catalogues = db.query(Catalogue).filter(Catalogue.menu_id == menu.id).all()
                for catalogue in catalogues:
                    existing = db.query(CatalogueRolePermission).filter(
                        CatalogueRolePermission.role_id == created_roles[role_name].id,
                        CatalogueRolePermission.catalogue_id == catalogue.id
                    ).first()
                    if not existing:
                        perm = CatalogueRolePermission(
                            role_id=created_roles[role_name].id,
                            catalogue_id=catalogue.id,
                            permission_type="admin"
                        )
                        db.add(perm)
                        print(f"Assigned admin permission on {catalogue.name} to {role_name}")
        
        db.commit()
        print("\nRole permissions assigned successfully!")
        
        # Create default categories
        categories_data = [
            {"name": "Storage", "description": "Storage automation catalogues", "icon": "storage", "display_order": 1},
            {"name": "Firewall", "description": "Firewall automation catalogues", "icon": "security", "display_order": 2},
            {"name": "Backup", "description": "Backup automation catalogues", "icon": "backup_restore", "display_order": 3},
            {"name": "Network", "description": "Network automation catalogues", "icon": "router", "display_order": 4},
            {"name": "Security", "description": "Security automation catalogues", "icon": "lock", "display_order": 5},
            {"name": "Monitoring", "description": "Monitoring automation catalogues", "icon": "monitoring", "display_order": 6},
            {"name": "Linux", "description": "Linux system management catalogues", "icon": "computer", "display_order": 7},
            {"name": "Other", "description": "Other automation catalogues", "icon": "folder", "display_order": 8},
        ]
        
        for cat_data in categories_data:
            existing = db.query(CatalogueCategory).filter(CatalogueCategory.name == cat_data["name"]).first()
            if not existing:
                category = CatalogueCategory(**cat_data)
                db.add(category)
                print(f"Created category: {cat_data['name']}")
            else:
                print(f"Category already exists: {cat_data['name']}")
        
        db.commit()
        print("\nCategories seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding menus: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_menus()
