"""
Script to create or update an admin user.
Usage: python scripts/create_admin.py <username>
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, get_engine
from app.models.user import User
from sqlalchemy import text

def ensure_sequences():
    """Ensure all required sequences exist"""
    engine = get_engine()
    if engine is None:
        return
    
    sequences = [
        'users_seq',
        'catalogue_categories_seq',
        'catalogues_seq',
        'roles_seq',
        'permissions_seq',
        'user_role_mapping_seq',
        'catalogue_permissions_seq'
    ]
    
    try:
        with engine.connect() as conn:
            for seq_name in sequences:
                try:
                    conn.execute(text(f"CREATE SEQUENCE {seq_name} START WITH 1 INCREMENT BY 1 NOCACHE"))
                    conn.commit()
                except Exception as e:
                    error_msg = str(e)
                    if "ORA-00955" not in error_msg and "already exists" not in error_msg.lower():
                        # Only log if it's not an "already exists" error
                        pass
                    conn.rollback()
    except Exception:
        pass  # Silently fail - sequences might already exist

def create_admin(username: str):
    """Create or update user to admin"""
    db = SessionLocal()
    if db is None:
        print("✗ Error: Database not available")
        sys.exit(1)
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if user:
            user.is_admin = True
            user.is_active = True
            db.commit()
            print(f"✓ User '{username}' updated to admin")
        else:
            # Create new admin user
            user = User(
                username=username,
                email=f"{username}@example.com",
                full_name=username,
                is_admin=True,
                is_active=True
            )
            db.add(user)
            db.commit()
            print(f"✓ Admin user '{username}' created")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_admin.py <username>")
        sys.exit(1)
    
    # Ensure sequences exist before creating user
    ensure_sequences()
    
    username = sys.argv[1]
    create_admin(username)

