#!/usr/bin/env python3
"""
Script to seed database with morning checklist test data.
This script creates sample data for the last 7 days with consistent hostnames
and command sets to ensure realistic "Success" (No Diff) and "Error" (Diff) scenarios.

Run this script after the database is set up:
    python scripts/seed_morning_checklist.py
"""
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import random
import copy

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.morning_checklist import MorningChecklist

# Sample hostnames
HOSTNAMES = [
    "web-server-01", "web-server-02", "db-server-01", "db-server-02",
    "app-server-01", "app-server-02", "cache-server-01", "load-balancer-01",
    "monitoring-server-01", "backup-server-01", "guaranteed-success-host"
]

# Sample IPs
IPS = [f"192.168.1.{i}" for i in range(10, 21)]

# Sample locations
LOCATIONS = [
    "Data Center A", "Data Center B", "Cloud Region US-East",
    "Cloud Region US-West", "On-Premise DC1", "On-Premise DC2"
]

# Sample applications
APPLICATIONS = [
    "Web Application", "Database Cluster", "API Gateway",
    "Cache Layer", "Load Balancer", "Monitoring System",
    "Backup System", "File Server", "Mail Server"
]

# Sample asset owners
ASSET_OWNERS = [
    "Infrastructure Team", "Database Team", "Application Team",
    "Network Team", "Security Team", "DevOps Team"
]

# Sample criticality levels
CRITICALITY = ["Critical", "High", "Medium", "Low"]

# Commands and their sample outputs
COMMANDS = {
    "Bond Interface Status": {
        "base": """bond0: flags=5187<UP,BROADCAST,RUNNING,MASTER,MULTICAST>  mtu 1500
        inet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255
        ether 00:1a:2b:3c:4d:5e  txqueuelen 0  (Ethernet)
        RX packets 1234567  bytes 987654321 (987.6 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 987654  bytes 123456789 (123.4 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0""",
        "error": """bond0: flags=5187<UP,BROADCAST,RUNNING,MASTER,MULTICAST>  mtu 1500
        inet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255
        RX errors 5  dropped 2  overruns 0  frame 3 [ERROR INCREASED]"""
    },
    "Disk Space Check": {
        "base": """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   25G   23G  53% /
/dev/sda2       100G   45G   50G  48% /var""",
        "error": """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   48G  500M  99% / [CRITICAL]
/dev/sda2       100G   95G  500M  96% /var"""
    },
    "Service Status Check": {
        "base": """● nginx.service - The nginx HTTP and reverse proxy server
   Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2024-12-09 10:00:00 UTC; 10h ago""",
        "error": """● nginx.service - The nginx HTTP and reverse proxy server
   Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since Mon 2024-12-09 20:00:00 UTC; 5min ago"""
    },
    "Load Average": {
        "base": "load average: 0.45, 0.52, 0.48",
        "error": "load average: 15.45, 12.52, 10.48 [HIGH LOAD]"
    }
}

MC_GROUPS = ["Network", "System", "Storage", "Application"]

def generate_host_config(hostname):
    """Generate a consistent configuration for a host"""
    random.seed(hostname) # Deterministic based on hostname
    
    config = {
        "hostname": hostname,
        "ip": random.choice(IPS),
        "location": random.choice(LOCATIONS),
        "application": random.choice(APPLICATIONS),
        "owner": random.choice(ASSET_OWNERS),
        "criticality": random.choice(CRITICALITY),
        "commands": random.sample(list(COMMANDS.keys()), k=3) # Pick 3 commands per host
    }
    return config

def seed_morning_checklist():
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        db.query(MorningChecklist).delete()
        db.commit()

        today = date.today()
        # Generate 7 days of data
        dates = [today - timedelta(days=i) for i in range(7)]
        dates.reverse() # Start from oldest to newest
        
        # Pre-generate configs for all hosts
        configs = {h: generate_host_config(h) for h in HOSTNAMES}
        
        # Store state of previous day {hostname: {cmd: output}}
        prev_day_state = {}

        total_entries = 0
        
        for check_date in dates:
            print(f"Generating for {check_date}...")
            
            for hostname in HOSTNAMES:
                config = configs[hostname]
                
                # Determine if this host has an issue TODAY
                # 80% Success (Match base/previous), 20% Error (Diff)
                # guaranteed-success-host is always success
                is_success = True
                if hostname != "guaranteed-success-host" and random.random() < 0.2:
                    is_success = False
                
                # For today's date, we might want more specific control?
                # User asked for "more success and errors for todays date"
                # The random chance above covers it, but let's force 50/50 for "web-server-01" today
                if check_date == today and hostname == "web-server-01":
                     is_success = False # Force an error for web-server-01 today
                
                current_state = {}
                entries = []
                
                for cmd in config["commands"]:
                    # Default to base output
                    output = COMMANDS[cmd]["base"]
                    
                    if not is_success:
                        # Introduce error/diff in one or more commands
                        # 50% chance per command to be the culprit if host is failing
                        if random.random() < 0.5:
                            output = COMMANDS[cmd]["error"]
                    
                    current_state[cmd] = output
                    
                    # Logic: 
                    # If current output == previous output -> NO_DIFF (Success)
                    # If current output != previous output -> DIFF (Error) (or just change)
                    # Note: First day has no previous, so it counts as new state (usually we consider it NO_DIFF or just ignore)
                    
                    prev_output = prev_day_state.get(hostname, {}).get(cmd, "")
                    
                    # Correctness Check:
                    # If we want "Success" in UI, we need NO diff.
                    # So current_state MUST equal prev_day_state.
                    # If `is_success` is True, we MUST use prev_output (if exists), otherwise base.
                    # Actually, if we stick to "Base" for success, and "Error" for failure:
                    # Day 1: Base
                    # Day 2: Base (Match -> Success)
                    # Day 3: Error (Diff -> Error)
                    # Day 4: Base (Diff -> Error? - technically yes, a diff from Error back to Base is a change)
                    # The UI treats ANY diff as an "issue" usually, or maybe just "Change detected".
                    # Let's assume "Success" means "Operating Normally" which usually implies "Base Output".
                    # If Day 3 was Error, Day 4 returning to Base is "Recovery". It shows a diff.
                    # To effectively toggle Success/Error:
                    # If we want Success, output = Base.
                    # If we want Error, output = Error.
                    # Wait, if Yesterday was Error, and Today is Base, that IS a diff.
                    # But the status (mc_status) is explicitly stored.
                    
                    mc_status = "reachable"
                    if not is_success: # We chose to simulate an error state
                         mc_status = "failed"
                         # output is already set to error variant
                    
                    # However, if we want to GUARANTEE "No Diff", we must match yesterday.
                    # If yesterday was Error, and today we want Success (No Diff), we must repeat Error?
                    # No, Success implies "Healthy". A Healthy system returning to health usually generates a Diff from the error state.
                    # The UI shows "Success" count based on `is_success` returned by `_compare_host`?
                    # backend: `_compare_host` returns `is_success` if `not has_diff`.
                    # So ANY change (even good ones) counts as !is_success (i.e. it goes to Error/Diff bucket).
                    # THIS IS KEY. Only Identical outputs go to "Success" bucket.
                    # So if we want Success bucket items, we need Identical Consecutive Days.
                    
                    # Strategy Adjustment:
                    # To get "Success" count > 0:
                    # We need Day N to match Day N-1.
                    # So if Day N-1 was Base, Day N must be Base.
                    # If Day N-1 was Error, Day N must be Error (Persistent Error).
                    
                    # To ensure stability:
                    # Most hosts should stay on Base.
                    # "guaranteed-success-host" will ALWAYS be Base.
                    
                    if is_success:
                        # Attempt to match previous state to ensure NO DIFF
                        if hostname in prev_day_state and cmd in prev_day_state[hostname]:
                             output = prev_day_state[hostname][cmd]
                        else:
                             output = COMMANDS[cmd]["base"]
                    else:
                        # We want a Diff. Force change from previous.
                        prev = prev_day_state.get(hostname, {}).get(cmd, COMMANDS[cmd]["base"])
                        if prev == COMMANDS[cmd]["base"]:
                             output = COMMANDS[cmd]["error"]
                        else:
                             output = COMMANDS[cmd]["base"] # Flip back to base to cause diff
                    
                    # Update current state map for THIS command
                    current_state[cmd] = output
                    
                    entry = MorningChecklist(
                        hostname=hostname,
                        ip=config["ip"],
                        location=config["location"],
                        application_name=config["application"],
                        asset_status="Active",
                        commands=cmd,
                        mc_output=output,
                        mc_group=random.choice(MC_GROUPS),
                        mc_check_date=check_date,
                        mc_status="failed" if not is_success else "reachable",
                        asset_owner=config["owner"],
                        mc_diff_status="DIFF" if not is_success else "NO_DIFF",
                        mc_criticality=config["criticality"],
                        updated_by="seed_script",
                        is_validated=False,
                        updated_at=datetime.utcnow()
                    )
                    entries.append(entry)
                
                # Update state for next day
                prev_day_state[hostname] = current_state
                db.add_all(entries)
                total_entries += len(entries)
                
            db.commit()
            
        print(f"Seeded {total_entries} entries.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_morning_checklist()

