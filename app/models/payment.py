from app.extensions import db
from sqlalchemy import event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

    # START: *** FIX ***
    # Make the invoice_id nullable to support legacy payments that don't have an invoice.
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)
    # END: *** FIX ***

    # These fields are now deprecated. We will remove them in a future migration.
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    cost_detail_id = db.Column(db.Integer, db.ForeignKey('cost_detail.id'), nullable=True)

    # Relationships
    invoice = db.relationship('Invoice', back_populates='payments')
    item = db.relationship('Item', backref=db.backref('legacy_payments', lazy=True))
    project = db.relationship('Project', backref=db.backref('legacy_payments', lazy=True))

    __table_args__ = (
        db.Index('idx_payment_project_id', 'project_id'),
        db.Index('idx_payment_item_id', 'item_id'),
        db.Index('idx_payment_cost_detail_id', 'cost_detail_id'),
        db.Index('idx_payment_invoice_id', 'invoice_id'),
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
        # The session is already in a flush process, so we just need to
        # make the change. The session commit that the user initiated
        # in the route will handle saving this change.
        target.invoice.update_status()