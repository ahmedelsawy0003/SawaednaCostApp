from app.extensions import db
from sqlalchemy import func
from app import constants # <-- إضافة جديدة

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), nullable=False, unique=True)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default=constants.INVOICE_STATUS_NEW) # <-- استخدام الثوابت
    notes = db.Column(db.Text)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=False)

    # Relationships
    project = db.relationship('Project', back_populates='invoices')
    contractor = db.relationship('Contractor', back_populates='invoices')
    items = db.relationship('InvoiceItem', back_populates='invoice', cascade="all, delete-orphan")
    payments = db.relationship('Payment', back_populates='invoice', cascade="all, delete-orphan")

    @property
    def total_amount(self):
        """Calculates the total amount of the invoice from its items."""
        return db.session.query(func.sum(InvoiceItem.total_price)).filter(InvoiceItem.invoice_id == self.id).scalar() or 0.0

    @property
    def paid_amount(self):
        """Calculates the total paid amount from associated payments."""
        return db.session.query(func.sum(Payment.amount)).filter(Payment.invoice_id == self.id).scalar() or 0.0

    @property
    def remaining_amount(self):
        """Calculates the remaining amount to be paid."""
        return self.total_amount - self.paid_amount

    def update_status(self):
        """Updates the invoice status based on its payments."""
        if self.status == constants.INVOICE_STATUS_CANCELLED: # <-- استخدام الثوابت
            return
            
        total = self.total_amount
        paid = self.paid_amount

        if paid <= 0:
            if self.status not in [constants.INVOICE_STATUS_NEW, constants.INVOICE_STATUS_UNDER_REVIEW, constants.INVOICE_STATUS_APPROVED]:
                 self.status = constants.INVOICE_STATUS_APPROVED
        elif paid >= total:
            self.status = constants.INVOICE_STATUS_FULLY_PAID # <-- استخدام الثوابت
        else:
            self.status = constants.INVOICE_STATUS_PARTIALLY_PAID # <-- استخدام الثوابت


    def __repr__(self):
        return f'<Invoice {self.invoice_number} for Project {self.project_id}>'

# Import related models at the bottom to avoid circular import issues
from .invoice_item import InvoiceItem
from .payment import Payment