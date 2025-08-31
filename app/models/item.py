from app.extensions import db
from sqlalchemy import func
from .payment import Payment
from .invoice_item import InvoiceItem
from .invoice import Invoice

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

    __table_args__ = (
        db.Index('idx_item_project_id', 'project_id'),
        db.Index('idx_item_contractor_id', 'contractor_id'),
    )

    @property
    def all_payments(self):
        """
        Fetches a list of all payments registered for this specific item
        across all its associated invoices.
        """
        # This property remains for the modal display, but the main calculation will be more robust.
        return Payment.query.join(
            InvoiceItem, Payment.invoice_item_id == InvoiceItem.id
        ).filter(
            InvoiceItem.item_id == self.id
        ).order_by(Payment.payment_date.desc()).all()

    @property
    def paid_amount(self):
        """
        Calculates the total paid amount for this item by proportionally
        distributing payments from all invoices it appears on.
        """
        total_paid_for_item = 0.0

        # Get all invoice items for this main item
        invoice_items = InvoiceItem.query.filter_by(item_id=self.id).all()
        
        # Get a set of unique invoice IDs to process each invoice only once
        invoice_ids = {ii.invoice_id for ii in invoice_items}

        for invoice_id in invoice_ids:
            invoice = Invoice.query.get(invoice_id)
            # Skip if invoice has no value or no payments
            if not invoice or invoice.total_amount == 0 or invoice.paid_amount == 0:
                continue

            # Get the total value of THIS item on THIS specific invoice
            value_of_this_item_on_invoice = db.session.query(
                func.sum(InvoiceItem.total_price)
            ).filter(
                InvoiceItem.invoice_id == invoice_id,
                InvoiceItem.item_id == self.id
            ).scalar() or 0.0
            
            # Calculate the proportion of this item's value relative to the invoice's total value
            proportion = value_of_this_item_on_invoice / invoice.total_amount
            
            # The amount paid for this item on this invoice is its proportion of the total amount paid on the invoice
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
        Calculates the actual total cost based on the sum of its value in all invoices.
        This represents the total invoiced amount for the item.
        """
        invoiced_amount = db.session.query(
            func.sum(InvoiceItem.total_price)
        ).filter(
            InvoiceItem.item_id == self.id
        ).scalar()
        
        # If the item has been invoiced, that is its actual cost.
        if invoiced_amount is not None:
            return invoiced_amount

        # Fallback for items not yet invoiced, using manual entry.
        if self.actual_quantity is not None and self.actual_unit_cost is not None:
             return self.actual_quantity * self.actual_unit_cost

        return 0.0
    
    @property
    def remaining_amount(self):
        """Calculates the remaining amount for the item based on actual cost and paid amount."""
        return self.actual_total_cost - self.paid_amount

    @property
    def cost_variance(self):
        return self.contract_total_cost - self.actual_total_cost

    @property
    def quantity_variance(self):
        if self.actual_quantity is not None:
            return self.contract_quantity - self.actual_quantity
        return self.contract_quantity
        
    @property
    def short_description(self):
        """Returns a truncated version of the description for display purposes."""
        if len(self.description) > 50:
            return self.description[:50] + '...'
        return self.description

    def __repr__(self):
        return f'<Item {self.item_number} - {self.description}>'