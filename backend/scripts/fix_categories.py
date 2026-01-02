import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Fixing catalogue_categories table...")
        # Oracle syntax active=1
        result = connection.execute(text("UPDATE catalogue_categories SET is_active = 1"))
        connection.commit()
        print(f"Updated {result.rowcount} rows. set is_active = 1")
        
        # Verify
        result = connection.execute(text("SELECT id, name, is_active, is_enabled FROM catalogue_categories"))
        rows = result.fetchall()
        print(f"Verification - Found {len(rows)} categories:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Active: {row[2]}, Enabled: {row[3]}")
                
except Exception as e:
    print(f"Error: {e}")
