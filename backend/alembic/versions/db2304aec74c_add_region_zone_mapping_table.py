"""Add region_zone_mapping table

Revision ID: db2304aec74c
Revises: 65ab1ca070b3
Create Date: 2025-12-23 07:19:21.534588

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "db2304aec74c"
down_revision = "65ab1ca070b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create region_zone_mapping table
    op.create_table(
        "region_zone_mapping",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("region_name", sa.String(length=100), nullable=False),
        sa.Column("zone_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Drop region_zone_mapping table
    op.drop_table("region_zone_mapping")

