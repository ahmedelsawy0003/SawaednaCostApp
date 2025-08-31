"""Consolidate database cleanup and updates

Revision ID: 6316c73746ab
Revises: ba9c6b63cd66 
Create Date: 2025-08-31 10:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6316c73746ab' # << تأكد من أن هذا الرقم يطابق اسم ملفك
down_revision = 'd57c7ec5dd05' # << هذا هو رقم المراجعة السابقة


def upgrade():
    # الخطوة 1: حذف عمود execution_method من جدول البنود
    with op.batch_alter_table('item', schema=None) as batch_op:
        batch_op.drop_column('execution_method')

    # الخطوة 2: إضافة الأعمدة الجديدة المطلوبة إلى جدول الدفعات أولاً
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('invoice_item_id', sa.Integer(), nullable=True))
        # نجعل الأعمدة القديمة قابلة لأن تكون فارغة مؤقتاً لتجنب الأخطاء
        batch_op.alter_column('item_id', existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column('project_id', existing_type=sa.INTEGER(), nullable=True)

    # الخطوة 3: إنشاء القيد (المفتاح الأجنبي) للعمود الجديد
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_payment_invoice_item_id', 'invoice_item', ['invoice_item_id'], ['id'])


def downgrade():
    # عكس العمليات بالترتيب المعاكس
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_constraint('fk_payment_invoice_item_id', type_='foreignkey')
        batch_op.drop_column('invoice_item_id')

    with op.batch_alter_table('item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('execution_method', sa.VARCHAR(length=100), autoincrement=False, nullable=True))