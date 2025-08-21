from app.extensions import db
from datetime import datetime
# لا تنس استيراد النموذج الجديد
from app.models.cost_detail import CostDetail

class Item(db.Model):
    """نموذج بند المشروع (مُحدّث)"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    # بيانات البند الأساسية (تبقى كما هي)
    item_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    # البيانات التعاقدية (تبقى كما هي)
    contract_quantity = db.Column(db.Float, nullable=False)
    contract_unit_cost = db.Column(db.Float, nullable=False)
    contract_total_cost = db.Column(db.Float, nullable=False)

    # بيانات التنفيذ (مع إزالة حقول التكلفة الفعلية)
    status = db.Column(db.String(20), default='نشط')
    execution_method = db.Column(db.String(50), nullable=True)
    contractor_name = db.Column(db.String(100), nullable=True)
    paid_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)

    # التواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة الجديدة مع تفاصيل التكلفة
    cost_details = db.relationship('CostDetail', backref='item', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def actual_total_cost(self):
        """(مُعدل) حساب التكلفة الفعلية الإجمالية من مجموع تفاصيل التكلفة"""
        return sum(detail.total_cost for detail in self.cost_details)

    @property
    def quantity_variance(self):
        """حساب الفرق في الكميات كخاصية"""
        # بما أن الكمية الفعلية لم تعد موجودة بشكل مباشر، يمكن تعديل هذه الدالة لاحقاً
        return 0

    @property
    def cost_variance(self):
        """حساب الفرق في التكاليف كخاصية"""
        return self.contract_total_cost - self.actual_total_cost

    @property
    def remaining_amount(self):
        """حساب المبلغ المتبقي كخاصية"""
        return self.actual_total_cost - (self.paid_amount or 0)

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
            'actual_total_cost': self.actual_total_cost, # سيتم حسابه تلقائياً
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