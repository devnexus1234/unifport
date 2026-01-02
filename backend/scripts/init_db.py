"""
Script to initialize the database with default categories and admin user.
Run this after setting up the database.
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, get_engine, Base
from app.models.catalogue import CatalogueCategory
from app.models.user import User

def init_db():
    """Initialize database with default data"""
    # Create all tables
    engine = get_engine()
    if engine is None:
        print("Warning: Database engine not available. Skipping table creation.")
        return
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    if db is None:
        print("Warning: Database session not available. Skipping initialization.")
        return
    try:
        # Create default categories
        categories = [
            {"name": "Storage", "description": "Storage automation catalogues", "icon": "storage", "display_order": 1},
            {"name": "Firewall", "description": "Firewall automation catalogues", "icon": "security", "display_order": 2},
            {"name": "Backup", "description": "Backup automation catalogues", "icon": "backup", "display_order": 3},
            {"name": "Network", "description": "Network automation catalogues", "icon": "router", "display_order": 4},
            {"name": "Security", "description": "Security automation catalogues", "icon": "lock", "display_order": 5},
            {"name": "Monitoring", "description": "Monitoring automation catalogues", "icon": "monitoring", "display_order": 6},
            {"name": "Other", "description": "Other automation catalogues", "icon": "folder", "display_order": 7},
        ]
        
        for cat_data in categories:
            existing = db.query(CatalogueCategory).filter(CatalogueCategory.name == cat_data["name"]).first()
            if not existing:
                category = CatalogueCategory(**cat_data)
                db.add(category)
        
        db.commit()
        print("Database initialized successfully!")
        print("Default categories created.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

