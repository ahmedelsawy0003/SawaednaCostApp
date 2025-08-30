from app.extensions import db
from sqlalchemy import func

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), nullable=False, unique=True)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default='جديد') # جديد، تحت المراجعة، معتمد، مدفوع جزئياً، مدفوع بالكامل، ملغي
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
        if self.status == 'ملغي':
            return
            
        total = self.total_amount
        paid = self.paid_amount

        if paid <= 0:
            # Keep status as is if it's 'جديد' or 'تحت المراجعة' or 'معتمد'
            if self.status not in ['جديد', 'تحت المراجعة', 'معتمد']:
                 self.status = 'معتمد' # Or whatever default approved status is
        elif paid >= total:
            self.status = 'مدفوع بالكامل'
        else:
            self.status = 'مدفوع جزئياً'


    def __repr__(self):
        return f'<Invoice {self.invoice_number} for Project {self.project_id}>'

# Import related models at the bottom to avoid circular import issues
from .invoice_item import InvoiceItem
from .payment import Payment