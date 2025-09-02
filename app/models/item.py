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
    
    @property
    def all_payments(self):
        """
        Fetches a list of all payments specifically linked to this item or its cost details.
        """
        # Get all invoice_item IDs related to this main item or its cost details
        related_invoice_item_ids_query = db.session.query(InvoiceItem.id).filter(
            or_(
                InvoiceItem.item_id == self.id,
                InvoiceItem.cost_detail.has(item_id=self.id)
            )
        )
        
        related_invoice_item_ids = [item[0] for item in related_invoice_item_ids_query.all()]

        if not related_invoice_item_ids:
            return []

        # Fetch only payments directly linked to those specific invoice_items
        direct_payments = Payment.query.filter(
            Payment.invoice_item_id.in_(related_invoice_item_ids)
        ).order_by(Payment.payment_date.desc()).all()
        
        return direct_payments
    
    @property
    def paid_amount(self):
        """
        Calculates the total paid amount for this item by summing up payments
        specifically linked to it, and its proportional share of general invoice payments.
        """
        total_paid_for_item = 0.0
        
        related_invoice_items = InvoiceItem.query.filter(
            or_(
                InvoiceItem.item_id == self.id,
                InvoiceItem.cost_detail.has(item_id=self.id)
            )
        ).all()
        
        invoice_map = {}
        for ii in related_invoice_items:
            if ii.invoice_id not in invoice_map:
                invoice_map[ii.invoice_id] = []
            invoice_map[ii.invoice_id].append(ii)

        for invoice_id, items_on_invoice in invoice_map.items():
            invoice = Invoice.query.get(invoice_id)
            if not invoice or invoice.total_amount == 0:
                continue

            value_of_this_item_on_invoice = sum(ii.total_price for ii in items_on_invoice)
            
            general_payments_on_invoice = db.session.query(func.sum(Payment.amount)).filter(
                Payment.invoice_id == invoice_id,
                Payment.invoice_item_id.is_(None)
            ).scalar() or 0.0

            if general_payments_on_invoice > 0:
                proportion = value_of_this_item_on_invoice / invoice.total_amount
                total_paid_for_item += general_payments_on_invoice * proportion

            related_invoice_item_ids = [ii.id for ii in items_on_invoice]
            direct_payments_to_item = db.session.query(func.sum(Payment.amount)).filter(
                Payment.invoice_item_id.in_(related_invoice_item_ids)
            ).scalar() or 0.0
            
            total_paid_for_item += direct_payments_to_item
            
        return total_paid_for_item

    @property
    def contract_total_cost(self):
        if self.contract_quantity is not None and self.contract_unit_cost is not None:
            return self.contract_quantity * self.contract_unit_cost
        return 0.0

    @property
    def actual_total_cost(self):
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

