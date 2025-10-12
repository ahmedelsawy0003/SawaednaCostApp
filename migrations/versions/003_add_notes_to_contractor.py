"""add notes to contractor

Revision ID: 003_add_notes_to_contractor

Revises: 002_add_vat_percent

Create Date: 2025-09-07 20:41:00

"""

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision = '003_add_notes_to_contractor'
down_revision = '002_add_vat_percent'
branch_labels = None
depends_on = None

def upgrade():
    # تم تعطيل السطر التالي لأن العمود "notes" موجود أصلاً في الجدول
    # with op.batch_alter_table('contractor', schema=None) as batch_op:
    #     batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
    pass

def downgrade():
    # إزالة العمود إذا رجعت للإصدار السابق لا يمثل مشكلة
    with op.batch_alter_table('contractor', schema=None) as batch_op:
        batch_op.drop_column('notes')
