"""add vat_percent to cost_detail

Revision ID: 002_add_vat_percent
Revises: 001_initial_and_vat_migration
Create Date: 2025-09-07 20:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = '002_add_vat_percent'
down_revision = '001_initial_and_vat_migration'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cost_detail', sa.Column('vat_percent', sa.Float(), server_default='0.0', nullable=False))


def downgrade():
    op.drop_column('cost_detail', 'vat_percent')