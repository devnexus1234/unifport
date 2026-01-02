"""
Script to test RBAC permissions for test users.
This script verifies that users can only see menus (categories) and catalogues they have access to.
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.catalogue import Catalogue, CatalogueCategory
from app.models.rbac import UserRole, CatalogueRolePermission

def test_rbac():
    """Test RBAC permissions for test users"""
    db = SessionLocal()
    if db is None:
        print("Warning: Database session not available.")
        return
    
    try:
        test_users = ["user1", "user2", "user3", "user4"]
        categories = db.query(CatalogueCategory).filter(CatalogueCategory.is_active == True).all()
        all_catalogues = db.query(Catalogue).filter(Catalogue.is_active == True).all()
        
        print("=" * 80)
        print("RBAC PERMISSION TEST")
        print("=" * 80)
        
        for username in test_users:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                print(f"\n❌ User '{username}' not found!")
                continue
            
            print(f"\n{'=' * 80}")
            print(f"Testing: {user.full_name} ({username})")
            print(f"{'=' * 80}")
            
            if user.is_admin:
                print("✓ User is ADMIN - should have access to all menus and catalogues")
                print(f"  Total categories: {len(categories)}")
                print(f"  Total catalogues: {len(all_catalogues)}")
                continue
            
            # Get user roles
            user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
            role_ids = [ur.role_id for ur in user_roles]
            
            if not role_ids:
                print("⚠ No roles assigned to user")
                continue
            
            # Check Menu (Category) Access via Catalogue Permissions
            accessible_categories_count = 0
            
            for category in categories:
                # Find catalogues in this category
                cat_catalogues = [c for c in all_catalogues if c.category_id == category.id]
                accessible_catalogues = []
                
                for catalogue in cat_catalogues:
                    # Check if user has role-based permission for this catalogue
                    perm = db.query(CatalogueRolePermission).filter(
                        CatalogueRolePermission.catalogue_id == catalogue.id,
                        CatalogueRolePermission.role_id.in_(role_ids)
                    ).first()
                    
                    if perm:
                        accessible_catalogues.append(catalogue)
                
                if accessible_catalogues:
                    accessible_categories_count += 1
                    print(f"\n✓ Menu: {category.name}")
                    print(f"  Catalogues ({len(accessible_catalogues)}):")
                    for cat in accessible_catalogues:
                        print(f"    - {cat.name}")
                # Else: category is hidden if no catalogues are accessible
            
            if accessible_categories_count == 0:
                print("⚠ No accessible menus")
            
            # Expected results (adjust based on actual seeded data if needed)
            print(f"\nExpected Results:")
            if username == "user2":
                print("  - Should see: Storage menu with all Storage catalogues")
            elif username == "user3":
                print("  - Should see: Storage and Firewall menus with all their catalogues")
            elif username == "user4":
                print("  - Should see: Backup menu with only 'Backup Configuration' catalogue")
        
        print(f"\n{'=' * 80}")
        print("TEST COMPLETE")
        print(f"{'=' * 80}")
        
    except Exception as e:
        print(f"Error testing RBAC: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_rbac()
