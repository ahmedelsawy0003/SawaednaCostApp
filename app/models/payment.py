from app.extensions import db
from sqlalchemy import event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'), nullable=True)

    # Relationships
    invoice = db.relationship('Invoice', back_populates='payments')
    invoice_item = db.relationship('InvoiceItem', back_populates='payments')
    
    __table_args__ = (
        db.Index('idx_payment_invoice_id', 'invoice_id'),
        db.Index('idx_payment_invoice_item_id', 'invoice_item_id'),
    )

    def __repr__(self):
        return f'<Payment {self.amount}>'

@event.listens_for(Payment, 'after_insert')
@event.listens_for(Payment, 'after_update')
@event.listens_for(Payment, 'after_delete')
def receive_after_payment_change(mapper, connection, target):
    if target.invoice:
        target.invoice.update_status()

from .invoice_item import InvoiceItem
