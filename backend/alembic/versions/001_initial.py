"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-10-21 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Initial migration - tables already exist."""
    pass


def downgrade():
    """Initial migration - no downgrade needed."""
    pass
