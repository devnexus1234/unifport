"""Add zone_device_mapping_network table

Revision ID: add_zone_device_mapping_network
Revises: add_capacity_network_values
Create Date: 2025-12-30 22:48:10.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_zone_device_mapping_network'
down_revision = 'add_capacity_network_values'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sequence for zone_device_mapping_network table
    op.execute("CREATE SEQUENCE zone_device_mapping_network_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    
    # Create zone_device_mapping_network table
    op.create_table(
        "zone_device_mapping_network",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("zone_name", sa.String(length=255), nullable=False),
        sa.Column("device_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Drop zone_device_mapping_network table
    op.drop_table("zone_device_mapping_network")
    
    # Drop sequence
    op.execute("DROP SEQUENCE zone_device_mapping_network_seq")
