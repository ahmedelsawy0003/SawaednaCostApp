from app.extensions import db
from sqlalchemy import func

class CostDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    
    description = db.Column(db.Text)
    unit = db.Column(db.String(50))
    quantity = db.Column(db.Float)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    
    # START: New Fields
    purchase_order = db.Column(db.String(255), nullable=True)
    payment_order = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=False, default='دفعة واحدة') # 'دفعة واحدة' or 'دفعات متعددة'
    
    # Foreign Key to link to the new Contractor model
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=True)
    # END: New Fields

    # This status is now deprecated as we will calculate it based on payments.
    # We will remove it in a later migration. For now, we set nullable=True.
    status = db.Column(db.String(50), nullable=True, server_default='غير مدفوع')

    item = db.relationship('Item', backref=db.backref('cost_details', lazy=True, cascade="all, delete-orphan"))
    
    # START: New Relationships
    contractor = db.relationship('Contractor', back_populates='cost_details')
    payments = db.relationship('Payment', backref='cost_detail', lazy='dynamic', cascade="all, delete-orphan")
    # END: New Relationships

    __table_args__ = (
        db.Index('idx_cost_detail_item_id', 'item_id'),
        # START: New Index
        db.Index('idx_cost_detail_contractor_id', 'contractor_id'),
        # END: New Index
    )

    # START: New Properties to calculate payment status
    @property
    def total_paid(self):
        """Calculates the sum of all payments made for this cost detail."""
        return db.session.query(func.sum(Payment.amount)).filter(Payment.cost_detail_id == self.id).scalar() or 0.0

    @property
    def remaining_amount(self):
        """Calculates the remaining amount to be paid."""
        return self.total_cost - self.total_paid

    @property
    def payment_status(self):
        """Determines the payment status based on payments."""
        if self.total_paid <= 0:
            return 'غير مدفوع'
        elif self.total_paid >= self.total_cost:
            return 'مدفوع بالكامل'
        else:
            return 'مدفوع جزئياً'
    # END: New Properties

    def __repr__(self):
        return f'<CostDetail {self.description} - {self.total_cost}>'

# We need the Payment model here for the property calculation
from .payment import Payment