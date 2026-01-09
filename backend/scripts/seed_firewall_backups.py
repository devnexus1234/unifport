import sys
from pathlib import Path
from datetime import date, timedelta
import random

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, get_engine, Base
from app.models.firewall_backup import FirewallBackup

def seed_firewall_backups():
    """Seed database with sample firewall backup data"""
    # Ensure table exists
    engine = get_engine()
    # if engine:
    #     Base.metadata.create_all(bind=engine)
    #     print("Ensured database tables exist.")

    db = SessionLocal()
    if db is None:
        print("Warning: Database session not available. Skipping seed.")
        return
    
    try:
        # Clear existing data
        db.query(FirewallBackup).delete()
        
        # Sample tasks
        tasks = [
            "Checkpoint_Management_Log_backup_REPORTS(BKC)",
            "Checkpoint Device Backup Report",
            "Checkpoint Configuration Backup Checkpoint Management IPs devices",
            "Cisco Configuration Backup Report of ASA FW devices(BSE-SAAS-FW only)",
            "Cisco Configuration Backup Report of ASA FW devices",
            "Cisco Configuration Backup Report of FTD devices",
            "F5 Configuration Backup Report of F5 SSLO devices",
            "Checkpoint Firewall Messages Backup (BKC)"
        ]
        
        # Generate data for past 10 days
        today = date.today()
        for i in range(10):
            current_date = today - timedelta(days=i)
            
            for task_name in tasks:
                # Randomize success/fail
                host_count = random.randint(1, 40)
                is_fail = random.random() < 0.2 # 20% chance of failure
                
                failed_count = random.randint(1, host_count) if is_fail else 0
                
                failed_hosts_list = []
                if failed_count > 0:
                    for j in range(failed_count):
                        failed_hosts_list.append(f"10.40.7.{random.randint(4, 20)}")
                
                failed_hosts = ", ".join(failed_hosts_list) if failed_hosts_list else None
                successful_hosts = f"{host_count - failed_count} Hosts" # Just simplified for CLOB
                
                backup = FirewallBackup(
                    task_date=current_date,
                    task_name=task_name,
                    host_count=host_count,
                    failed_count=failed_count,
                    failed_hosts=failed_hosts,
                    successful_hosts=successful_hosts
                )
                db.add(backup)
        
        db.commit()
        print("Firewall backup data seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding firewall backups: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_firewall_backups()
