"""
Script to seed database with sample users and assign multiple roles to them.
This script creates catalogue-specific roles based on existing catalogues and assigns them to users.
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
from app.models.rbac import Role, UserRole, CatalogueRolePermission

def seed_users():
    """Seed database with sample users and assign multiple roles based on catalogues"""
    db = SessionLocal()
    if db is None:
        print("Warning: Database session not available. Skipping seed.")
        return
    
    try:
        # Get all catalogues from database
        catalogues = db.query(Catalogue).filter(Catalogue.is_active == True).all()
        
        if not catalogues:
            print("No catalogues found. Please run seed_menus.py first to create catalogues.")
            return
        
        print(f"Found {len(catalogues)} catalogues. Creating catalogue-specific roles...")
        
        # Create roles for each catalogue (Admin and User roles)
        roles = {}
        for catalogue in catalogues:
            # Create Admin role for catalogue
            admin_role_name = f"{catalogue.name} Admin"
            admin_role = db.query(Role).filter(Role.name == admin_role_name).first()
            if not admin_role:
                admin_role = Role(
                    name=admin_role_name,
                    description=f"Full access to {catalogue.name} catalogue",
                    is_active=True
                )
                db.add(admin_role)
                db.flush()
                print(f"Created role: {admin_role_name}")
            roles[admin_role_name] = admin_role
            
            # Create User role for catalogue
            user_role_name = f"{catalogue.name} User"
            user_role = db.query(Role).filter(Role.name == user_role_name).first()
            if not user_role:
                user_role = Role(
                    name=user_role_name,
                    description=f"Read access to {catalogue.name} catalogue",
                    is_active=True
                )
                db.add(user_role)
                db.flush()
                print(f"Created role: {user_role_name}")
            roles[user_role_name] = user_role
            
            # Assign catalogue permissions to roles
            # Admin role gets admin permission
            existing_admin_perm = db.query(CatalogueRolePermission).filter(
                CatalogueRolePermission.role_id == admin_role.id,
                CatalogueRolePermission.catalogue_id == catalogue.id
            ).first()
            if not existing_admin_perm:
                admin_perm = CatalogueRolePermission(
                    role_id=admin_role.id,
                    catalogue_id=catalogue.id,
                    permission_type="admin"
                )
                db.add(admin_perm)
            
            # User role gets read permission
            existing_user_perm = db.query(CatalogueRolePermission).filter(
                CatalogueRolePermission.role_id == user_role.id,
                CatalogueRolePermission.catalogue_id == catalogue.id
            ).first()
            if not existing_user_perm:
                user_perm = CatalogueRolePermission(
                    role_id=user_role.id,
                    catalogue_id=catalogue.id,
                    permission_type="read"
                )
                db.add(user_perm)
        
        db.commit()
        print(f"Created {len(roles)} catalogue-specific roles.\n")
        
        # Map catalogues to role names for easier assignment
        catalogue_role_map = {}
        for catalogue in catalogues:
            catalogue_role_map[catalogue.name] = {
                "admin": f"{catalogue.name} Admin",
                "user": f"{catalogue.name} User"
            }
        
        # Define users with their catalogue-specific roles
        # Roles are assigned based on catalogues: Storage Provisioning, Storage Monitoring, 
        # Backup Configuration, Backup Restore, Firewall Rules, Firewall Logs,
        # Linux Server Management, Linux Package Management
        users_data = [
            {
                "username": "john.doe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Provisioning Admin", "Storage Monitoring Admin", "Backup Configuration User", "Firewall Rules User"]
            },
            {
                "username": "jane.smith",
                "email": "jane.smith@example.com",
                "full_name": "Jane Smith",
                "is_admin": False,
                "is_active": True,
                "roles": ["Backup Configuration Admin", "Backup Restore Admin", "Storage Provisioning User", "Linux Server Management User"]
            },
            {
                "username": "bob.wilson",
                "email": "bob.wilson@example.com",
                "full_name": "Bob Wilson",
                "is_admin": False,
                "is_active": True,
                "roles": ["Firewall Rules Admin", "Firewall Logs Admin", "Linux Server Management Admin", "Storage Monitoring User"]
            },
            {
                "username": "alice.brown",
                "email": "alice.brown@example.com",
                "full_name": "Alice Brown",
                "is_admin": False,
                "is_active": True,
                "roles": ["Linux Server Management Admin", "Linux Package Management Admin", "Backup Restore Admin", "Firewall Logs User"]
            },
            {
                "username": "charlie.davis",
                "email": "charlie.davis@example.com",
                "full_name": "Charlie Davis",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Provisioning User", "Storage Monitoring User", "Backup Configuration User", "Backup Restore User", "Firewall Rules User", "Firewall Logs User", "Linux Server Management User", "Linux Package Management User"]
            },
            {
                "username": "diana.miller",
                "email": "diana.miller@example.com",
                "full_name": "Diana Miller",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Provisioning Admin", "Storage Monitoring Admin", "Backup Configuration Admin", "Backup Restore Admin"]
            },
            {
                "username": "edward.taylor",
                "email": "edward.taylor@example.com",
                "full_name": "Edward Taylor",
                "is_admin": False,
                "is_active": True,
                "roles": ["Firewall Rules Admin", "Firewall Logs Admin", "Linux Package Management User", "Storage Provisioning User"]
            },
            {
                "username": "fiona.anderson",
                "email": "fiona.anderson@example.com",
                "full_name": "Fiona Anderson",
                "is_admin": False,
                "is_active": True,
                "roles": ["Linux Server Management Admin", "Linux Package Management Admin", "Storage Monitoring User", "Backup Restore User"]
            },
            {
                "username": "george.martinez",
                "email": "george.martinez@example.com",
                "full_name": "George Martinez",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Provisioning Admin", "Storage Monitoring Admin", "Firewall Rules Admin", "Firewall Logs Admin", "Linux Server Management Admin", "Linux Package Management Admin"]
            },
            {
                "username": "helen.thomas",
                "email": "helen.thomas@example.com",
                "full_name": "Helen Thomas",
                "is_admin": False,
                "is_active": True,
                "roles": ["Backup Configuration Admin", "Backup Restore Admin", "Firewall Logs User", "Linux Package Management User"]
            },
            {
                "username": "ivan.jackson",
                "email": "ivan.jackson@example.com",
                "full_name": "Ivan Jackson",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Provisioning User", "Storage Monitoring User", "Backup Configuration User", "Backup Restore User"]
            },
            {
                "username": "julia.white",
                "email": "julia.white@example.com",
                "full_name": "Julia White",
                "is_admin": False,
                "is_active": True,
                "roles": ["Firewall Rules Admin", "Firewall Logs Admin", "Backup Configuration Admin", "Backup Restore Admin", "Storage Monitoring User", "Linux Server Management User"]
            },
            {
                "username": "kevin.harris",
                "email": "kevin.harris@example.com",
                "full_name": "Kevin Harris",
                "is_admin": False,
                "is_active": True,
                "roles": ["Linux Server Management Admin", "Linux Package Management Admin", "Firewall Rules User"]
            },
            {
                "username": "linda.clark",
                "email": "linda.clark@example.com",
                "full_name": "Linda Clark",
                "is_admin": False,
                "is_active": True,
                "roles": ["Storage Provisioning Admin", "Storage Monitoring Admin", "Backup Restore User", "Firewall Logs User", "Linux Package Management User"]
            },
            {
                "username": "michael.lewis",
                "email": "michael.lewis@example.com",
                "full_name": "Michael Lewis",
                "is_admin": False,
                "is_active": True,
                "roles": ["Backup Configuration Admin", "Backup Restore Admin", "Storage Provisioning Admin", "Storage Monitoring Admin", "Linux Server Management Admin", "Linux Package Management Admin"]
            }
        ]
        
        created_users = {}
        for user_data in users_data:
            roles_list = user_data.pop("roles")  # Remove roles from user data
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                print(f"User already exists: {user_data['username']}")
                created_users[user_data["username"]] = existing_user
                # Update user info if needed
                for key, value in user_data.items():
                    setattr(existing_user, key, value)
                db.flush()
            else:
                # Create new user
                user = User(**user_data)
                db.add(user)
                db.flush()  # Get the ID
                created_users[user_data["username"]] = user
                print(f"Created user: {user_data['username']} ({user_data['full_name']})")
            
            # Assign roles to user
            user = created_users[user_data["username"]]
            for role_name in roles_list:
                if role_name in roles:
                    # Check if role assignment already exists
                    existing_assignment = db.query(UserRole).filter(
                        UserRole.user_id == user.id,
                        UserRole.role_id == roles[role_name].id
                    ).first()
                    
                    if not existing_assignment:
                        user_role = UserRole(
                            user_id=user.id,
                            role_id=roles[role_name].id,
                            is_dl=False
                        )
                        db.add(user_role)
                        print(f"  Assigned role: {role_name}")
                    else:
                        print(f"  Role already assigned: {role_name}")
                else:
                    print(f"  Warning: Role '{role_name}' not found. Make sure catalogues are created first.")
        
        db.commit()
        print(f"\n✓ Successfully seeded {len(created_users)} users with multiple roles!")
        print("\nSummary:")
        for username, user in created_users.items():
            user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
            role_names = [db.query(Role).filter(Role.id == ur.role_id).first().name 
                         for ur in user_roles if db.query(Role).filter(Role.id == ur.role_id).first()]
            print(f"  - {user.full_name} ({username}): {', '.join(role_names)}")
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
