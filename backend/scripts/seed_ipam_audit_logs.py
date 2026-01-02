import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.ipam import IpamAuditLog, IpamAllocation, IpamSegment
from app.models.user import User

def seed_audit_logs():
    db = SessionLocal()
    try:
        # Get a user (or create dummy one if needed, but assuming users exist from other seeds)
        user = db.query(User).first()
        if not user:
            print("No users found. Please seed users first.")
            return

        # Get some allocations
        allocations = db.query(IpamAllocation).limit(20).all()
        if not allocations:
            print("No allocations found. Please seed IPAM data first.")
            return

        print(f"Seeding audit logs for user {user.username}...")
        
        actions = ["UPDATE_ALLOCATION", "ASSIGN_IP", "RELEASE_IP", "UPDATE_COMMENT"]
        
        for alloc in allocations:
            # Create 1-3 logs per allocation
            for _ in range(random.randint(1, 3)):
                action = random.choice(actions)
                changes = ""
                
                if action == "UPDATE_ALLOCATION":
                    changes = "Status: Unassigned -> Assigned, RITM: None -> RITM12345"
                elif action == "ASSIGN_IP":
                    changes = "Assigned status: Assigned"
                elif action == "RELEASE_IP":
                    changes = "Status: Assigned -> Unassigned"
                elif action == "UPDATE_COMMENT":
                    changes = "Comment: Updated comment for testing"
                
                # Random time in past 30 days
                random_days = random.randint(0, 30)
                created_at = datetime.now() - timedelta(days=random_days)

                log = IpamAuditLog(
                    user_id=user.id,
                    segment_id=alloc.segment_id,
                    ip_address=alloc.ip_address,
                    action=action,
                    changes=changes,
                    created_at=created_at
                )
                db.add(log)
        
        db.commit()
        print("Successfully seeded IPAM audit logs.")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_audit_logs()
