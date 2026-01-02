"""Insert demo data for network capacity tables

Revision ID: insert_demo_data_network
Revises: add_region_zone_mapping_network
Create Date: 2025-12-30 22:48:30.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'insert_demo_data_network'
down_revision = 'add_region_zone_mapping_network'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Insert demo data into region_zone_mapping_network (copy from region_zone_mapping)
    conn.execute(text("""
        INSERT INTO region_zone_mapping_network (id, region_name, zone_name)
        SELECT region_zone_mapping_network_seq.NEXTVAL, region_name, zone_name
        FROM region_zone_mapping
    """))
    
    # Insert demo data into zone_device_mapping_network (copy from zone_device_mapping)
    conn.execute(text("""
        INSERT INTO zone_device_mapping_network (id, zone_name, device_name)
        SELECT zone_device_mapping_network_seq.NEXTVAL, zone_name, device_name
        FROM zone_device_mapping
    """))
    
    # Insert demo data into capacity_network_values (copy from capacity_values, excluding connection fields)
    conn.execute(text("""
        INSERT INTO capacity_network_values (
            id, device_name, mean_cpu, peak_cpu, mean_memory, peak_memory,
            cpu_date, cpu_time, memory_date, memory_time,
            cpu_alert_duration, memory_alert_duration, ntimes_cpu, ntimes_memory
        )
        SELECT 
            capacity_network_values_seq.NEXTVAL, device_name, mean_cpu, peak_cpu, 
            mean_memory, peak_memory, cpu_date, cpu_time, memory_date, memory_time,
            cpu_alert_duration, memory_alert_duration, ntimes_cpu, ntimes_memory
        FROM capacity_values
    """))


def downgrade() -> None:
    conn = op.get_bind()
    
    # Delete demo data
    conn.execute(text("DELETE FROM capacity_network_values"))
    conn.execute(text("DELETE FROM zone_device_mapping_network"))
    conn.execute(text("DELETE FROM region_zone_mapping_network"))
