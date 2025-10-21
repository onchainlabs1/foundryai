"""Add DPIA linkage fields

Revision ID: 005_add_dpia_fields
Revises: 004_add_model_versions
Create Date: 2025-10-21 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_dpia_fields'
down_revision = '004_add_model_versions'
branch_labels = None
depends_on = None


def upgrade():
    """Add DPIA linkage fields."""
    # Add dpia_link to ai_systems
    op.add_column('ai_systems', sa.Column('dpia_link', sa.String(500), nullable=True))
    
    # Add dpia_reference to fria
    op.add_column('fria', sa.Column('dpia_reference', sa.String(500), nullable=True))


def downgrade():
    """Remove DPIA linkage fields."""
    op.drop_column('fria', 'dpia_reference')
    op.drop_column('ai_systems', 'dpia_link')
