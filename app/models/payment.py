from app.extensions import db
from sqlalchemy import event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)
    
    # --- START: REMOVED OLD RELATIONSHIP ---
    # The direct link to a single invoice_item is no longer needed.
    # invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'), nullable=True)
    # --- END: REMOVED OLD RELATIONSHIP ---

    # Relationships
    invoice = db.relationship('Invoice', back_populates='payments')
    
    # --- START: NEW RELATIONSHIP ---
    # A payment is now linked to its many distributions
    distributions = db.relationship('PaymentDistribution', back_populates='payment', cascade="all, delete-orphan")
    # --- END: NEW RELATIONSHIP ---
    
    __table_args__ = (
        db.Index('idx_payment_invoice_id', 'invoice_id'),
        # db.Index('idx_payment_invoice_item_id', 'invoice_item_id'), # No longer needed
    )

    def __repr__(self):
        return f'<Payment {self.amount}>'

@event.listens_for(Payment, 'after_insert')
@event.listens_for(Payment, 'after_update')
@event.listens_for(Payment, 'after_delete')
def receive_after_payment_change(mapper, connection, target):
    if target.invoice:
        db.session.flush()
        target.invoice.update_status()

# We need to import the related models at the bottom to avoid circular imports
from .invoice_item import InvoiceItem
from .payment_distribution import PaymentDistribution
