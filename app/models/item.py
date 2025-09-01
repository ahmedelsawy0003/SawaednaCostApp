from app.extensions import db
from sqlalchemy import func, or_
from .payment import Payment
from .invoice_item import InvoiceItem
from .invoice import Invoice
from .cost_detail import CostDetail

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

    # --- START: تعديل منطق عرض الدفعات ---
    @property
    def all_payments(self):
        """
        Fetches a list of all payments related to this item.
        It includes payments linked directly to the invoice_item and
        payments linked to the parent invoice in general.
        """
        # 1. Find all invoices where this item appears
        invoice_ids_subquery = db.session.query(InvoiceItem.invoice_id).filter(InvoiceItem.item_id == self.id).distinct()
        
        # 2. Find all payments linked to those invoices
        payments = Payment.query.filter(
            Payment.invoice_id.in_(invoice_ids_subquery)
        ).order_by(Payment.payment_date.desc()).all()
        
        return payments
    # --- END: تعديل منطق عرض الدفعات ---

    @property
    def paid_amount(self):
        """
        Calculates the total paid amount for this item by proportionally
        distributing payments from all invoices it appears on.
        """
        total_paid_for_item = 0.0
        invoice_items = InvoiceItem.query.filter_by(item_id=self.id).all()
        invoice_ids = {ii.invoice_id for ii in invoice_items}

        for invoice_id in invoice_ids:
            invoice = Invoice.query.get(invoice_id)
            if not invoice or invoice.total_amount == 0 or invoice.paid_amount == 0:
                continue

            value_of_this_item_on_invoice = db.session.query(
                func.sum(InvoiceItem.total_price)
            ).filter(
                InvoiceItem.invoice_id == invoice_id,
                InvoiceItem.item_id == self.id
            ).scalar() or 0.0
            
            proportion = value_of_this_item_on_invoice / invoice.total_amount
            paid_for_this_item_on_this_invoice = invoice.paid_amount * proportion
            total_paid_for_item += paid_for_this_item_on_this_invoice
            
        return total_paid_for_item

    @property
    def contract_total_cost(self):
        if self.contract_quantity is not None and self.contract_unit_cost is not None:
            return self.contract_quantity * self.contract_unit_cost
        return 0.0

    @property
    def actual_total_cost(self):
        """
        Calculates the actual total cost. 
        Priority 1: Sum of all associated cost_details.
        Priority 2: Manually entered actual_quantity * actual_unit_cost if no details exist.
        """
        total_from_details = db.session.query(
            func.sum(CostDetail.quantity * CostDetail.unit_cost)
        ).filter(CostDetail.item_id == self.id).scalar()

        if total_from_details is not None and total_from_details > 0:
            return total_from_details

        if self.actual_quantity is not None and self.actual_unit_cost is not None:
            return self.actual_quantity * self.actual_unit_cost

        return 0.0
    
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