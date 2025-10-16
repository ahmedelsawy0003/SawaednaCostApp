from app.extensions import db
from sqlalchemy import func
from .payment_distribution import PaymentDistribution

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    cost_detail_id = db.Column(db.Integer, db.ForeignKey('cost_detail.id'), nullable=True)

    # Relationships
    invoice = db.relationship('Invoice', back_populates='items')
    item = db.relationship('Item', back_populates='invoice_items')
    cost_detail = db.relationship('CostDetail', backref=db.backref('invoice_items', lazy=True))
    
    # --- START: REMOVED OLD RELATIONSHIP ---
    # The direct link from a payment is no longer needed.
    # payments = db.relationship('Payment', back_populates='invoice_item', cascade="all, delete-orphan")
    # --- END: REMOVED OLD RELATIONSHIP ---

    # --- START: NEW RELATIONSHIP ---
    # An invoice item can have many payment distributions
    distributions = db.relationship('PaymentDistribution', back_populates='invoice_item', cascade="all, delete-orphan")
    # --- END: NEW RELATIONSHIP ---

    @property
    def paid_amount(self):
        """Calculates the total amount paid specifically for this invoice item."""
        if not self.id:
            return 0.0
        return db.session.query(
            func.sum(PaymentDistribution.amount)
        ).filter(
            PaymentDistribution.invoice_item_id == self.id
        ).scalar() or 0.0

    @property
    def remaining_amount(self):
        """Calculates the remaining amount for this invoice item."""
        return self.total_price - self.paid_amount

    def __init__(self, quantity, item=None, cost_detail=None):
        if item:
            self.item = item
            self.description = f"{item.item_number} - {item.description}"
            actual_cost = item.actual_unit_cost
            contract_cost = item.contract_unit_cost
            self.unit_price = actual_cost if actual_cost is not None and actual_cost > 0 else (contract_cost or 0.0)
        elif cost_detail:
            self.cost_detail = cost_detail
            self.item = cost_detail.item
            self.description = f"تفصيل: {cost_detail.description}"
            # --- START: FIX VAT IN UNIT PRICE FOR COST DETAIL ---
            # Calculate unit price including VAT for accurate invoicing
            self.unit_price = cost_detail.total_cost / cost_detail.quantity if cost_detail.quantity > 0 else 0.0
            # --- END: FIX VAT IN UNIT PRICE FOR COST DETAIL ---
        else:
            raise ValueError("InvoiceItem must be initialized with either an 'item' or a 'cost_detail'.")

        self.quantity = quantity
        self.total_price = (self.quantity or 0.0) * self.unit_price

    def __repr__(self):
        return f'<InvoiceItem for Item {self.item_id} on Invoice {self.invoice_id}>'