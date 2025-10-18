"""Merge multiple heads for final upgrade

Revision ID: ca08b07f2401
Revises: 22a5c9c70461, add_new_models
Create Date: 2025-10-18 17:31:10.042731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca08b07f2401'
down_revision = ('22a5c9c70461', 'add_new_models')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
