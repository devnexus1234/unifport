"""merge_heads

Revision ID: fee76fcc934c
Revises: 923833e46dcb, add_network_capacity_catalogue
Create Date: 2026-01-09 12:06:07.426575

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fee76fcc934c'
down_revision = ('923833e46dcb', 'add_network_capacity_catalogue')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

