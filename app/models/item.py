from app.extensions import db
from sqlalchemy import func
from .payment import Payment
from .invoice_item import InvoiceItem
from .invoice import Invoice

# --- START: استيراد الموديل الجديد ---
from .cost_detail import CostDetail
# --- END: استيراد الموديل الجديد ---

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

    # --- START: العلاقة الجديدة مع تفاصيل التكاليف ---
    cost_details = db.relationship('CostDetail', back_populates='item', lazy='dynamic', cascade="all, delete-orphan")
    # --- END: العلاقة الجديدة ---

    __table_args__ = (
        db.Index('idx_item_project_id', 'project_id'),
        db.Index('idx_item_contractor_id', 'contractor_id'),
    )

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

    # --- START: المنطق الجديد والمعدل لحساب التكلفة الفعلية ---
    @property
    def actual_total_cost(self):
        """
        Calculates the actual total cost. 
        Priority 1: Sum of all associated cost_details.
        Priority 2: Manually entered actual_quantity * actual_unit_cost if no details exist.
        """
        # الأولوية الأولى: حساب المجموع من تفاصيل التكاليف
        total_from_details = db.session.query(
            func.sum(CostDetail.quantity * CostDetail.unit_cost)
        ).filter(CostDetail.item_id == self.id).scalar()

        # إذا كان هناك مجموع من التفاصيل، قم بإرجاعه
        if total_from_details is not None and total_from_details > 0:
            return total_from_details

        # الأولوية الثانية (الاحتياطية): استخدام الإدخال اليدوي
        if self.actual_quantity is not None and self.actual_unit_cost is not None:
            return self.actual_quantity * self.actual_unit_cost

        # إذا لم يتوفر أي مما سبق، فالتكلفة هي صفر
        return 0.0
    # --- END: المنطق الجديد ---
    
    @property
    def remaining_amount(self):
        """Calculates the remaining amount for the item based on actual cost and paid amount."""
        # ملاحظة: هذا الرقم قد لا يكون له معنى محاسبي دقيق الآن بعد فصل الأنظمة
        # لكن يمكن استخدامه كمؤشر عام.
        return self.actual_total_cost - self.paid_amount

    @property
    def cost_variance(self):
        return self.contract_total_cost - self.actual_total_cost
        
    @property
    def short_description(self):
        """Returns a truncated version of the description for display purposes."""
        if len(self.description) > 50:
            return self.description[:50] + '...'
        return self.description

    def __repr__(self):
        return f'<Item {self.item_number} - {self.description}>'