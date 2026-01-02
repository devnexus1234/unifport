"""Add zone_device_mapping table

Revision ID: 923833e46dcb
Revises: db2304aec74c
Create Date: 2025-12-23 07:26:01.905067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "923833e46dcb"
down_revision = "db2304aec74c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create zone_device_mapping table
    op.create_table(
        "zone_device_mapping",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("zone_name", sa.String(length=255), nullable=False),
        sa.Column("device_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Drop zone_device_mapping table
    op.drop_table("zone_device_mapping")

