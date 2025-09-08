from app.extensions import db
from sqlalchemy import func, or_, select
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property
from .payment import Payment
from .invoice_item import InvoiceItem
from .invoice import Invoice
from .cost_detail import CostDetail
from .payment_distribution import PaymentDistribution
from app import constants

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    item_number = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50))
    contract_quantity = db.Column(db.Float)
    contract_unit_cost = db.Column(db.Float)
    actual_quantity = db.Column(db.Float)
    actual_unit_cost = db.Column(db.Float)
    status = db.Column(db.String(50), default=constants.ITEM_STATUS_ACTIVE)
    notes = db.Column(db.Text)
    
    purchase_order_number = db.Column(db.String(100), nullable=True)
    disbursement_order_number = db.Column(db.String(100), nullable=True)

    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=True)

    project = db.relationship('Project', back_populates='items')
    contractor = db.relationship('Contractor', back_populates='items')
    cost_details = db.relationship('CostDetail', back_populates='item', cascade="all, delete-orphan")

    __table_args__ = (
        db.Index('idx_item_project_id', 'project_id'),
        db.Index('idx_item_contractor_id', 'contractor_id'),
    )
    
    # --- START: PERFORMANCE & WARNING FIXES ---

    # This property calculates the details cost efficiently at the DB level
    actual_details_cost = column_property(
        select(func.coalesce(func.sum(CostDetail.quantity * CostDetail.unit_cost * (1 + CostDetail.vat_percent / 100)), 0.0))
        .where(CostDetail.item_id == id)
        .correlate_except(CostDetail)
        .scalar_subquery(),
        deferred=True  # Load it only when needed or explicitly requested
    )

    @property
    def all_payments(self):
        invoice_item_ids = db.session.query(InvoiceItem.id).filter(InvoiceItem.item_id == self.id)
        distributions = PaymentDistribution.query.filter(
            PaymentDistribution.invoice_item_id.in_(invoice_item_ids)
        ).all()
        return distributions

    @property
    def paid_amount(self):
        # Using select() to prevent SAWarning
        invoice_item_ids_query = select(InvoiceItem.id).filter(InvoiceItem.item_id == self.id)
        total_paid = db.session.query(
            func.sum(PaymentDistribution.amount)
        ).filter(
            PaymentDistribution.invoice_item_id.in_(invoice_item_ids_query)
        ).scalar()
        return total_paid or 0.0

    @property
    def contract_total_cost(self):
        if self.contract_quantity is not None and self.contract_unit_cost is not None:
            return self.contract_quantity * self.contract_unit_cost
        return 0.0

    # This hybrid property now uses the efficient column_property
    @hybrid_property
    def actual_total_cost(self):
        manual_cost = 0.0
        if self.actual_quantity is not None and self.actual_unit_cost is not None:
            manual_cost = self.actual_quantity * self.actual_unit_cost
        
        return manual_cost + (self.actual_details_cost or 0.0)
    
    # --- END: PERFORMANCE & WARNING FIXES ---

    @property
    def remaining_amount(self):
        return self.actual_total_cost - self.paid_amount

    @property
    def cost_variance(self):
        return self.contract_total_cost - self.actual_total_cost
        
    @property
    def short_description(self):
        if len(self.description) > 50:
            return self.description[:50] + '...'
        return self.description

    def __repr__(self):
        return f'<Item {self.item_number} - {self.description}>'