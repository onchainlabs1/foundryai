"""Add model versions table for change management

Revision ID: 004_add_model_versions
Revises: 003_add_eu_db_status
Create Date: 2025-10-21 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_model_versions'
down_revision = '003_add_eu_db_status'
branch_labels = None
depends_on = None


def upgrade():
    """Create model_versions table."""
    op.create_table(
        'model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('released_at', sa.DateTime(), nullable=False),
        sa.Column('approver_email', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('artifact_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['system_id'], ['ai_systems.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_model_versions_org_system', 'model_versions', ['org_id', 'system_id'])


def downgrade():
    """Drop model_versions table."""
    op.drop_index('ix_model_versions_org_system', table_name='model_versions')
    op.drop_table('model_versions')
