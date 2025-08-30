from app.extensions import db
from sqlalchemy import event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

    # START: *** CRITICAL CHANGE ***
    # The payment is now linked directly to an invoice.
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    # END: *** CRITICAL CHANGE ***

    # These fields are now deprecated. We will remove them in a future migration.
    # For now, we make them nullable to avoid breaking old data immediately.
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    cost_detail_id = db.Column(db.Integer, db.ForeignKey('cost_detail.id'), nullable=True)


    # Relationships
    # A payment belongs to one invoice.
    invoice = db.relationship('Invoice', back_populates='payments')
    
    # Deprecated relationships, will be removed later.
    item = db.relationship('Item', backref=db.backref('legacy_payments', lazy=True))
    project = db.relationship('Project', backref=db.backref('legacy_payments', lazy=True))


    __table_args__ = (
        # These indexes on deprecated columns can also be removed later.
        db.Index('idx_payment_project_id', 'project_id'),
        db.Index('idx_payment_item_id', 'item_id'),
        db.Index('idx_payment_cost_detail_id', 'cost_detail_id'),
        # START: New Index for the invoice link
        db.Index('idx_payment_invoice_id', 'invoice_id'),
        # END: New Index
    )

    def __repr__(self):
        return f'<Payment {self.amount} for Invoice {self.invoice_id}>'

# Add an event listener to automatically update the invoice status after a payment is made or deleted.
@event.listens_for(Payment, 'after_insert')
@event.listens_for(Payment, 'after_update')
@event.listens_for(Payment, 'after_delete')
def receive_after_payment_change(mapper, connection, target):
    """After a payment is saved or deleted, update the parent invoice's status."""
    if target.invoice:
        target.invoice.update_status()
        # You might need to explicitly commit the session if the event is not within a session flush
        # from sqlalchemy.orm import object_session
        # session = object_session(target)
        # if session:
        #     session.commit()