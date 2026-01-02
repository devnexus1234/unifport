"""Add capacity_values table

Revision ID: aac9b7c1d084
Revises: 864dc67102c0
Create Date: 2025-12-23 06:07:10.551281

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import oracle

# revision identifiers, used by Alembic.
revision = 'aac9b7c1d084'
down_revision = '864dc67102c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sequence for capacity_values table
    op.execute("CREATE SEQUENCE capacity_values_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    
    # Create capacity_values table
    op.create_table('capacity_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=True),
        sa.Column('mean_cpu', sa.Float(), nullable=True),
        sa.Column('peak_cpu', sa.Float(), nullable=True),
        sa.Column('mean_memory', sa.Float(), nullable=True),
        sa.Column('peak_memory', sa.Float(), nullable=True),
        sa.Column('mean_connection', sa.Float(), nullable=True),
        sa.Column('peak_connection', sa.Float(), nullable=True),
        sa.Column('cpu_date', sa.String(length=255), nullable=True),
        sa.Column('cpu_time', sa.String(length=255), nullable=True),
        sa.Column('memory_date', sa.String(length=255), nullable=True),
        sa.Column('memory_time', sa.String(length=255), nullable=True),
        sa.Column('cpu_alert_threshold', sa.Float(), nullable=True),
        sa.Column('memory_alert_threshold', sa.Float(), nullable=True),
        sa.Column('ntimes_cpu', sa.Integer(), nullable=True),
        sa.Column('ntimes_memory', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop capacity_values table
    op.drop_table('capacity_values')
    
    # Drop sequence
    op.execute("DROP SEQUENCE capacity_values_seq")

