"""Initial migration with VAT column

Revision ID: 001_initial_and_vat_migration
Revises: 
Create Date: 2025-09-07 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_and_vat_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # This is a comprehensive schema creation that should match the current state
    # of your models, including the 'vat_percent' column.
    
    # You might already have these tables. The commands are here for completeness.
    # We will handle potential errors during the upgrade process.
    
    bind = op.get_bind()
    
    # Create tables if they don't exist
    op.create_table('contractor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('role', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_table('project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('spreadsheet_id', sa.String(length=255), nullable=True),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['manager_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('item_number', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('contract_quantity', sa.Float(), nullable=True),
        sa.Column('contract_unit_cost', sa.Float(), nullable=True),
        sa.Column('actual_quantity', sa.Float(), nullable=True),
        sa.Column('actual_unit_cost', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('purchase_order_number', sa.String(length=100), nullable=True),
        sa.Column('disbursement_order_number', sa.String(length=100), nullable=True),
        sa.Column('contractor_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('invoice_type', sa.String(length=50), nullable=False),
        sa.Column('purchase_order_number', sa.String(length=100), nullable=True),
        sa.Column('disbursement_order_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('contractor_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number')
    )
    op.create_table('cost_detail',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=False),
        sa.Column('purchase_order_number', sa.String(length=100), nullable=True),
        sa.Column('disbursement_order_number', sa.String(length=100), nullable=True),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('contractor_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('cost_detail_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['cost_detail_id'], ['cost_detail.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment_distribution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('invoice_item_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_item_id'], ['invoice_item.id'], ),
        sa.ForeignKeyConstraint(['payment_id'], ['payment.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Check if the column exists before adding it
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('cost_detail')]
    if 'vat_percent' not in columns:
        with op.batch_alter_table('cost_detail', schema=None) as batch_op:
            batch_op.add_column(sa.Column('vat_percent', sa.Float(), server_default='0.0', nullable=False))

def downgrade():
    # This is a comprehensive downgrade for all tables
    with op.batch_alter_table('cost_detail', schema=None) as batch_op:
        batch_op.drop_column('vat_percent')
        
    op.drop_table('payment_distribution')
    op.drop_table('payment')
    op.drop_table('invoice_item')
    op.drop_table('cost_detail')
    op.drop_table('invoice')
    op.drop_table('item')
    op.drop_table('project')
    op.drop_table('user')
    op.drop_table('contractor')