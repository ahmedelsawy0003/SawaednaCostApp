from app.extensions import db
from sqlalchemy import func
from .payment import Payment
from .invoice_item import InvoiceItem

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
    # --- START: حذف حقل غير مستخدم ---
    # execution_method لم يعد مستخدماً في النماذج الجديدة
    # execution_method = db.Column(db.String(100))
    # --- END: حذف حقل غير مستخدم ---
    notes = db.Column(db.Text)
    
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=True)

    project = db.relationship('Project', backref=db.backref('items', lazy=True, cascade="all, delete-orphan"))
    contractor = db.relationship('Contractor', back_populates='items')

    __table_args__ = (
        db.Index('idx_item_project_id', 'project_id'),
        db.Index('idx_item_contractor_id', 'contractor_id'),
    )

    @property
    def paid_amount(self):
        """
        يحسب إجمالي المبلغ المدفوع لهذا البند المحدد
        عن طريق جمع كل الدفعات المرتبطة بظهور هذا البند في كل الفواتير.
        """
        total_paid = db.session.query(func.sum(Payment.amount)).join(
            InvoiceItem, Payment.invoice_item_id == InvoiceItem.id
        ).filter(
            InvoiceItem.item_id == self.id
        ).scalar()
        return total_paid or 0.0

    @property
    def contract_total_cost(self):
        if self.contract_quantity is not None and self.contract_unit_cost is not None:
            return self.contract_quantity * self.contract_unit_cost
        return 0.0

    # --- START: تعديل منطق التكلفة الفعلية ---
    @property
    def actual_total_cost(self):
        """
        يحسب التكلفة الإجمالية الفعلية. إذا لم يتم إدخالها، 
        فإنها تساوي المبلغ المدفوع تلقائياً.
        """
        # التحقق إذا كانت هناك قيمة مدخلة يدوياً
        manual_actual_cost = 0.0
        if self.actual_quantity is not None and self.actual_unit_cost is not None:
            manual_actual_cost = self.actual_quantity * self.actual_unit_cost

        # إذا كانت القيمة المدخلة يدوياً أكبر من صفر، نستخدمها
        if manual_actual_cost > 0:
            return manual_actual_cost
        
        # إذا لم تكن هناك قيمة مدخلة، نستخدم المبلغ المدفوع كتكلفة فعلية
        return self.paid_amount
    # --- END: تعديل منطق التكلفة الفعلية ---

    @property
    def remaining_amount(self):
        """يحسب المبلغ المتبقي للبند بناءً على التكلفة الفعلية والمبلغ المدفوع."""
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