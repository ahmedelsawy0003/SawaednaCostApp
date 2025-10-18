"""Add new models for forms, payment orders, and BOQ

Revision ID: add_new_models
Revises: 
Create Date: 2025-10-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_new_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create sequence_counter table
    op.create_table('sequence_counter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prefix', sa.String(length=10), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('current_number', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('prefix', 'year', name='uq_prefix_year')
    )
    op.create_index(op.f('ix_sequence_counter_prefix'), 'sequence_counter', ['prefix'], unique=False)
    op.create_index(op.f('ix_sequence_counter_year'), 'sequence_counter', ['year'], unique=False)

    # Create material_request table
    op.create_table('material_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_number', sa.String(length=20), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('boq_item_id', sa.Integer(), nullable=True),
    sa.Column('request_date', sa.Date(), nullable=False),
    sa.Column('requester_id', sa.Integer(), nullable=False),
    sa.Column('project_manager_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('approved_by_id', sa.Integer(), nullable=True),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['approved_by_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['boq_item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['project_manager_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('request_number')
    )
    op.create_index(op.f('ix_material_request_request_number'), 'material_request', ['request_number'], unique=True)

    # Create material_request_item table
    op.create_table('material_request_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('boq_item_number', sa.String(length=50), nullable=True),
    sa.Column('material_name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.Column('quantity_available', sa.Float(), nullable=True),
    sa.Column('quantity_requested', sa.Float(), nullable=False),
    sa.Column('required_date', sa.Date(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['request_id'], ['material_request.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create material_return table
    op.create_table('material_return',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('return_number', sa.String(length=20), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('boq_item_id', sa.Integer(), nullable=True),
    sa.Column('return_date', sa.Date(), nullable=False),
    sa.Column('requester_id', sa.Integer(), nullable=False),
    sa.Column('project_manager_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('approved_by_id', sa.Integer(), nullable=True),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['approved_by_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['boq_item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['project_manager_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('return_number')
    )
    op.create_index(op.f('ix_material_return_return_number'), 'material_return', ['return_number'], unique=True)

    # Create material_return_item table
    op.create_table('material_return_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('return_id', sa.Integer(), nullable=False),
    sa.Column('boq_item_number', sa.String(length=50), nullable=True),
    sa.Column('material_name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['return_id'], ['material_return.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create payment_order table
    op.create_table('payment_order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('payment_number', sa.String(length=20), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('boq_item_id', sa.Integer(), nullable=True),
    sa.Column('payment_type', sa.String(length=50), nullable=False),
    sa.Column('beneficiary', sa.String(length=200), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('payment_date', sa.Date(), nullable=False),
    sa.Column('requester_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('approved_by_id', sa.Integer(), nullable=True),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('paid_by_id', sa.Integer(), nullable=True),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.Column('payment_method', sa.String(length=50), nullable=True),
    sa.Column('reference_number', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['approved_by_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['boq_item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['paid_by_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('payment_number')
    )
    op.create_index(op.f('ix_payment_order_payment_number'), 'payment_order', ['payment_number'], unique=True)

    # Create boq_item table
    op.create_table('boq_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('item_number', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('executed_quantity', sa.Float(), nullable=True),
    sa.Column('unit_price', sa.Float(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('completion_percentage', sa.Float(), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('boq_item')
    op.drop_index(op.f('ix_payment_order_payment_number'), table_name='payment_order')
    op.drop_table('payment_order')
    op.drop_table('material_return_item')
    op.drop_index(op.f('ix_material_return_return_number'), table_name='material_return')
    op.drop_table('material_return')
    op.drop_table('material_request_item')
    op.drop_index(op.f('ix_material_request_request_number'), table_name='material_request')
    op.drop_table('material_request')
    op.drop_index(op.f('ix_sequence_counter_year'), table_name='sequence_counter')
    op.drop_index(op.f('ix_sequence_counter_prefix'), table_name='sequence_counter')
    op.drop_table('sequence_counter')
