#!/usr/bin/env python3
"""
Script to ensure all required Oracle sequences exist.
This fixes the ORA-02289 error when sequences don't exist.
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_engine
from sqlalchemy import text

def ensure_sequences():
    """Create all required sequences if they don't exist"""
    sequences = [
        'users_seq',
        'catalogue_categories_seq',
        'catalogues_seq',
        'roles_seq',
        'permissions_seq',
        'user_role_mapping_seq',
        'catalogue_permissions_seq',
        'zone_device_mapping_seq',
        'region_zone_mapping_seq'
    ]
    
    engine = get_engine()
    if engine is None:
        print("✗ Error: Database engine not available")
        sys.exit(1)
    
    try:
        with engine.connect() as conn:
            for seq_name in sequences:
                try:
                    # Try to create the sequence
                    conn.execute(text(f"CREATE SEQUENCE {seq_name} START WITH 1 INCREMENT BY 1 NOCACHE"))
                    conn.commit()
                    print(f"✓ Created sequence: {seq_name}")
                except Exception as e:
                    error_msg = str(e)
                    if "ORA-00955" in error_msg or "already exists" in error_msg.lower():
                        print(f"  Sequence {seq_name} already exists (skipping)")
                    else:
                        print(f"✗ Error creating {seq_name}: {e}")
                        # Try to continue with other sequences
                        conn.rollback()
            
            # Verify sequences exist
            print("\nVerifying sequences...")
            result = conn.execute(text("SELECT sequence_name FROM user_sequences WHERE sequence_name LIKE '%_SEQ' ORDER BY sequence_name"))
            existing = [row[0] for row in result]
            print(f"Found {len(existing)} sequences:")
            for seq in existing:
                print(f"  - {seq}")
            
            print("\n✓ Sequences check complete!")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ensure_sequences()
