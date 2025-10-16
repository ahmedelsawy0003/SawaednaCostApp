from app.extensions import db
from sqlalchemy import func, select # <<< تم إضافة select
from app import constants
from sqlalchemy.orm import relationship, column_property # <<< تم إضافة column_property

# Make sure to import related models at the top
from .invoice_item import InvoiceItem
from .payment import Payment

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), nullable=False, unique=True)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default=constants.INVOICE_STATUS_NEW)
    
    invoice_type = db.Column(db.String(50), nullable=False, default='مقاول') # الأنواع: مقاول، مورد، شراء مباشر
    purchase_order_number = db.Column(db.String(100), nullable=True)
    disbursement_order_number = db.Column(db.String(100), nullable=True)
    
    notes = db.Column(db.Text)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=False)

    project = relationship('Project', back_populates='invoices')
    contractor = relationship('Contractor', back_populates='invoices')
    items = relationship('InvoiceItem', back_populates='invoice', cascade="all, delete-orphan")
    payments = relationship('Payment', back_populates='invoice', cascade="all, delete-orphan")

    # --- START: Performance Refactoring using column_property ---
    # حساب الإجمالي الكلي لبنود الفاتورة بكفاءة عالية (في استعلام القائمة)
    total_amount = column_property(
        select(func.coalesce(func.sum(InvoiceItem.total_price), 0.0))
        .where(InvoiceItem.invoice_id == id)
        .correlate_except(InvoiceItem)
        .scalar_subquery(),
        deferred=True
    )
    
    # حساب إجمالي المدفوعات على الفاتورة بكفاءة عالية
    paid_amount = column_property(
        select(func.coalesce(func.sum(Payment.amount), 0.0))
        .where(Payment.invoice_id == id)
        .correlate_except(Payment)
        .scalar_subquery(),
        deferred=True
    )
    # --- END: Performance Refactoring ---

    @property
    def remaining_amount(self):
        # Now relies on column_property attributes
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self):
        # Using a small tolerance for float comparison
        return self.remaining_amount < 0.01

    def update_status(self):
        if self.status == constants.INVOICE_STATUS_CANCELLED:
            return
        total = self.total_amount
        paid = self.paid_amount
        if paid <= 0:
            # Keep the current status if it's New, Under Review, or Approved
            if self.status not in [constants.INVOICE_STATUS_NEW, constants.INVOICE_STATUS_UNDER_REVIEW, constants.INVOICE_STATUS_APPROVED]:
                self.status = constants.INVOICE_STATUS_APPROVED
        elif paid >= total:
            self.status = constants.INVOICE_STATUS_FULLY_PAID
        else:
            self.status = constants.INVOICE_STATUS_PARTIALLY_PAID

    def __repr__(self):
        return f'<Invoice {self.invoice_number} for Project {self.project_id}>'