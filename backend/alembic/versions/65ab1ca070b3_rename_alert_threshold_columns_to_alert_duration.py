"""Rename alert threshold columns to alert duration in capacity_values

Revision ID: 65ab1ca070b3
Revises: aac9b7c1d084
Create Date: 2025-12-23 06:13:51.929882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65ab1ca070b3'
down_revision = 'aac9b7c1d084'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename columns in capacity_values table
    op.execute("ALTER TABLE capacity_values RENAME COLUMN cpu_alert_threshold TO cpu_alert_duration")
    op.execute("ALTER TABLE capacity_values RENAME COLUMN memory_alert_threshold TO memory_alert_duration")


def downgrade() -> None:
    # Rename columns back to original names
    op.execute("ALTER TABLE capacity_values RENAME COLUMN cpu_alert_duration TO cpu_alert_threshold")
    op.execute("ALTER TABLE capacity_values RENAME COLUMN memory_alert_duration TO memory_alert_threshold")

