"""Add Network Capacity Report catalogue

Revision ID: add_network_capacity_catalogue
Revises: insert_demo_data_network
Create Date: 2025-12-30 22:48:40.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'add_network_capacity_catalogue'
down_revision = 'insert_demo_data_network'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Get Network category_id
    result = conn.execute(text("SELECT id FROM catalogue_categories WHERE name = 'Network'"))
    row = result.fetchone()
    
    if row:
        network_category_id = row[0]
        
        # Insert Network Capacity Report catalogue
        conn.execute(text("""
            INSERT INTO catalogues (
                id, name, description, category_id, api_endpoint, 
                frontend_route, icon, is_enabled, is_active, display_order
            ) VALUES (
                catalogues_seq.NEXTVAL,
                'Network Capacity Report',
                'Network infrastructure capacity monitoring and reporting',
                :category_id,
                '/api/v1/capacity-network-report',
                'catalogues/capacity-network-report',
                'network_check',
                1,
                1,
                0
            )
        """), {"category_id": network_category_id})
    else:
        # If Network category doesn't exist, create it first
        conn.execute(text("""
            INSERT INTO catalogue_categories (
                id, name, description, icon, display_order, is_enabled, is_active
            ) VALUES (
                catalogue_categories_seq.NEXTVAL,
                'Network',
                'Network related catalogues',
                'router',
                4,
                1,
                1
            )
        """))
        
        # Get the newly created category_id
        result = conn.execute(text("SELECT id FROM catalogue_categories WHERE name = 'Network'"))
        row = result.fetchone()
        network_category_id = row[0]
        
        # Insert Network Capacity Report catalogue
        conn.execute(text("""
            INSERT INTO catalogues (
                id, name, description, category_id, api_endpoint, 
                frontend_route, icon, is_enabled, is_active, display_order
            ) VALUES (
                catalogues_seq.NEXTVAL,
                'Network Capacity Report',
                'Network infrastructure capacity monitoring and reporting',
                :category_id,
                '/api/v1/capacity-network-report',
                'catalogues/capacity-network-report',
                'network_check',
                1,
                1,
                0
            )
        """), {"category_id": network_category_id})


def downgrade() -> None:
    conn = op.get_bind()
    
    # Delete Network Capacity Report catalogue
    conn.execute(text("DELETE FROM catalogues WHERE name = 'Network Capacity Report'"))
