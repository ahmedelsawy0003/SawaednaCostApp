from app.extensions import db
from datetime import datetime

class Item(db.Model):
    """نموذج بند المشروع (مُحدّث)"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    item_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    contract_quantity = db.Column(db.Float, nullable=False)
    contract_unit_cost = db.Column(db.Float, nullable=False)
    contract_total_cost = db.Column(db.Float, nullable=False)

    actual_quantity = db.Column(db.Float, nullable=True)
    
    # **** هذا هو الحقل الجديد الذي سيتم إدخاله يدوياً ****
    actual_unit_cost = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(20), default='نشط')
    execution_method = db.Column(db.String(50), nullable=True)
    contractor_name = db.Column(db.String(100), nullable=True)
    paid_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cost_details = db.relationship('CostDetail', backref='item', lazy='dynamic', cascade='all, delete-orphan')

    # **** تم تغيير منطق هذه الدالة بالكامل ****
    @property
    def actual_total_cost(self):
        """(مُعدل) حساب التكلفة الإجمالية الفعلية من حاصل ضرب الكمية في سعر الوحدة المدخل يدوياً"""
        quantity = self.actual_quantity or 0
        unit_cost = self.actual_unit_cost or 0
        return quantity * unit_cost

    # **** تم حذف الدالة الحسابية السابقة لـ actual_unit_cost ****

    @property
    def quantity_variance(self):
        """حساب الفرق في الكميات كخاصية"""
        if self.actual_quantity is not None:
             return self.actual_quantity - self.contract_quantity
        return 0

    @property
    def cost_variance(self):
        """حساب الفرق في التكاليف كخاصية"""
        return self.contract_total_cost - self.actual_total_cost

    @property
    def remaining_amount(self):
        """حساب المبلغ المتبقي كخاصية"""
        # تم تعديلها لتعتمد على المدفوعات فقط بالنسبة للبند
        paid_amount = self.paid_amount or 0
        return self.actual_total_cost - paid_amount

    def to_dict(self):
        """تحويل البند إلى قاموس (مُحدّث)"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'item_number': self.item_number,
            'description': self.description,
            'unit': self.unit,
            'contract_quantity': self.contract_quantity,
            'contract_unit_cost': self.contract_unit_cost,
            'contract_total_cost': self.contract_total_cost,
            'actual_quantity': self.actual_quantity,
            'actual_unit_cost': self.actual_unit_cost,
            'actual_total_cost': self.actual_total_cost,
            'quantity_variance': self.quantity_variance,
            'cost_variance': self.cost_variance,
            'status': self.status,
            'execution_method': self.execution_method,
            'contractor_name': self.contractor_name,
            'paid_amount': self.paid_amount,
            'remaining_amount': self.remaining_amount,
            'notes': self.notes,
            'cost_details': [detail.to_dict() for detail in self.cost_details],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }