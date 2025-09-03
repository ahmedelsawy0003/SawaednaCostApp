from app.extensions import db
from sqlalchemy import func, or_
from .payment import Payment
from .invoice_item import InvoiceItem
from .invoice import Invoice
from .cost_detail import CostDetail
# --- START: Import the new PaymentDistribution model ---
from .payment_distribution import PaymentDistribution
# --- END: Import the new PaymentDistribution model ---

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
    status = db.Column(db.String(50), default='نشط')
    notes = db.Column(db.Text)
    
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=True)

    project = db.relationship('Project', back_populates='items')
    contractor = db.relationship('Contractor', back_populates='items')
    cost_details = db.relationship('CostDetail', back_populates='item', lazy='dynamic', cascade="all, delete-orphan")

    __table_args__ = (
        db.Index('idx_item_project_id', 'project_id'),
        db.Index('idx_item_contractor_id', 'contractor_id'),
    )
    
    # --- START: Updated all_payments property ---
    @property
    def all_payments(self):
        """
        Fetches a list of all payment distributions related to this item.
        """
        # Subquery to get invoice_item_ids for the current main item
        invoice_item_ids = db.session.query(InvoiceItem.id).filter(InvoiceItem.item_id == self.id)
        
        # Query PaymentDistribution for distributions linked to those invoice_items
        distributions = PaymentDistribution.query.filter(
            PaymentDistribution.invoice_item_id.in_(invoice_item_ids)
        ).all()
        
        return distributions
    # --- END: Updated all_payments property ---


    # --- START: Updated paid_amount property ---
    @property
    def paid_amount(self):
        """
        Calculates the total paid amount for this item by summing up
        all its related payment distributions.
        """
        # Subquery to get all invoice_item IDs associated with this main item
        invoice_item_ids_subquery = db.session.query(InvoiceItem.id).filter(InvoiceItem.item_id == self.id).subquery()

        # Sum the amounts from PaymentDistribution where invoice_item_id is in our subquery
        total_paid = db.session.query(
            func.sum(PaymentDistribution.amount)
        ).filter(
            PaymentDistribution.invoice_item_id.in_(invoice_item_ids_subquery)
        ).scalar()
        
        return total_paid or 0.0
    # --- END: Updated paid_amount property ---


    @property
    def contract_total_cost(self):
        if self.contract_quantity is not None and self.contract_unit_cost is not None:
            return self.contract_quantity * self.contract_unit_cost
        return 0.0

    # --- START: التعديل الرئيسي حسب طلبك ---
    @property
    def actual_total_cost(self):
        if self.actual_quantity is not None and self.actual_unit_cost is not None:
            return self.actual_quantity * self.actual_unit_cost
        return 0.0
    # --- END: التعديل الرئيسي ---
    
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

