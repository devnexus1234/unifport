"""Add region_zone_mapping_network table

Revision ID: add_region_zone_mapping_network
Revises: add_zone_device_mapping_network
Create Date: 2025-12-30 22:48:20.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_region_zone_mapping_network'
down_revision = 'add_zone_device_mapping_network'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sequence for region_zone_mapping_network table
    op.execute("CREATE SEQUENCE region_zone_mapping_network_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    
    # Create region_zone_mapping_network table
    op.create_table(
        "region_zone_mapping_network",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("region_name", sa.String(length=100), nullable=False),
        sa.Column("zone_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Drop region_zone_mapping_network table
    op.drop_table("region_zone_mapping_network")
    
    # Drop sequence
    op.execute("DROP SEQUENCE region_zone_mapping_network_seq")
