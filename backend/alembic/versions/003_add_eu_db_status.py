"""Add EU Database status field

Revision ID: 003_add_eu_db_status
Revises: 002_add_fria_extended_fields
Create Date: 2025-10-21 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_eu_db_status'
down_revision = '002_add_fria_extended_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add EU Database status field."""
    op.add_column('ai_systems', sa.Column('eu_db_status', sa.String(50), nullable=True, default='pending'))


def downgrade():
    """Remove EU Database status field."""
    op.drop_column('ai_systems', 'eu_db_status')
