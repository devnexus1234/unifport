"""Add capacity_network_values table

Revision ID: add_capacity_network_values
Revises: db2304aec74c
Create Date: 2025-12-30 22:48:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import oracle

# revision identifiers, used by Alembic.
revision = 'add_capacity_network_values'
down_revision = 'db2304aec74c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sequence for capacity_network_values table
    op.execute("CREATE SEQUENCE capacity_network_values_seq START WITH 1 INCREMENT BY 1 NOCACHE")
    
    # Create capacity_network_values table (without connection fields)
    op.create_table('capacity_network_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_name', sa.String(length=255), nullable=True),
        sa.Column('mean_cpu', sa.Float(), nullable=True),
        sa.Column('peak_cpu', sa.Float(), nullable=True),
        sa.Column('mean_memory', sa.Float(), nullable=True),
        sa.Column('peak_memory', sa.Float(), nullable=True),
        sa.Column('cpu_date', sa.String(length=255), nullable=True),
        sa.Column('cpu_time', sa.String(length=255), nullable=True),
        sa.Column('memory_date', sa.String(length=255), nullable=True),
        sa.Column('memory_time', sa.String(length=255), nullable=True),
        sa.Column('cpu_alert_duration', sa.Float(), nullable=True),
        sa.Column('memory_alert_duration', sa.Float(), nullable=True),
        sa.Column('ntimes_cpu', sa.Integer(), nullable=True),
        sa.Column('ntimes_memory', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop capacity_network_values table
    op.drop_table('capacity_network_values')
    
    # Drop sequence
    op.execute("DROP SEQUENCE capacity_network_values_seq")
