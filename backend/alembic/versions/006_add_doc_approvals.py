"""Add document approvals table

Revision ID: 006_add_doc_approvals
Revises: 005_add_dpia_fields
Create Date: 2025-10-21 21:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_doc_approvals'
down_revision = '005_add_dpia_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Create doc_approvals table."""
    op.create_table(
        'doc_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('doc_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='draft'),
        sa.Column('submitted_by', sa.String(255), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approver_email', sa.String(255), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('document_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['system_id'], ['ai_systems.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_doc_approvals_org_system', 'doc_approvals', ['org_id', 'system_id'])
    op.create_index('ix_doc_approvals_doc_type', 'doc_approvals', ['org_id', 'system_id', 'doc_type'])


def downgrade():
    """Drop doc_approvals table."""
    op.drop_index('ix_doc_approvals_doc_type', table_name='doc_approvals')
    op.drop_index('ix_doc_approvals_org_system', table_name='doc_approvals')
    op.drop_table('doc_approvals')
