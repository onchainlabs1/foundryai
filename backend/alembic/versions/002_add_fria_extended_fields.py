"""Add extended FRIA fields for audit-grade compliance

Revision ID: 002_add_fria_extended_fields
Revises: 001_initial
Create Date: 2025-10-21 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_fria_extended_fields'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """Add extended FRIA fields."""
    # Add new columns to FRIA table
    op.add_column('fria', sa.Column('ctx_json', sa.Text(), nullable=True))
    op.add_column('fria', sa.Column('risks_json', sa.Text(), nullable=True))
    op.add_column('fria', sa.Column('safeguards_json', sa.Text(), nullable=True))
    op.add_column('fria', sa.Column('proportionality', sa.Text(), nullable=True))
    op.add_column('fria', sa.Column('residual_risk', sa.String(50), nullable=True))
    op.add_column('fria', sa.Column('review_notes', sa.Text(), nullable=True))


def downgrade():
    """Remove extended FRIA fields."""
    # Remove new columns from FRIA table
    op.drop_column('fria', 'review_notes')
    op.drop_column('fria', 'residual_risk')
    op.drop_column('fria', 'proportionality')
    op.drop_column('fria', 'safeguards_json')
    op.drop_column('fria', 'risks_json')
    op.drop_column('fria', 'ctx_json')
