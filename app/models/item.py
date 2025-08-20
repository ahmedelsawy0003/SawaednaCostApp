from app.extensions import db
from datetime import datetime

class Item(db.Model):
    """نموذج بند المشروع"""
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # بيانات البند الأساسية
    item_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    
    # البيانات التعاقدية
    contract_quantity = db.Column(db.Float, nullable=False)
    contract_unit_cost = db.Column(db.Float, nullable=False)
    contract_total_cost = db.Column(db.Float, nullable=False)
    
    # البيانات الفعلية
    actual_quantity = db.Column(db.Float, nullable=True)
    actual_unit_cost = db.Column(db.Float, nullable=True)
    actual_total_cost = db.Column(db.Float, nullable=True)
    
    # بيانات التنفيذ
    status = db.Column(db.String(20), default='نشط')  # نشط، مكتمل، متوقف
    execution_method = db.Column(db.String(50), nullable=True)  # تنفيذ مباشر، تعاقد من الباطن
    contractor_name = db.Column(db.String(100), nullable=True)
    paid_amount = db.Column(db.Float, default=0)
    remaining_amount = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # التواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Item {self.item_number}: {self.description}>'
    
    def to_dict(self):
        """تحويل البند إلى قاموس"""
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
            'quantity_variance': self.get_quantity_variance(),
            'cost_variance': self.get_cost_variance(),
            'status': self.status,
            'execution_method': self.execution_method,
            'contractor_name': self.contractor_name,
            'paid_amount': self.paid_amount,
            'remaining_amount': self.remaining_amount,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_quantity_variance(self):
        """حساب الفرق في الكميات"""
        if self.actual_quantity is None:
            return 0
        return self.contract_quantity - self.actual_quantity
    
    def get_cost_variance(self):
        """حساب الفرق في التكاليف"""
        if self.actual_total_cost is None:
            return 0
        return self.contract_total_cost - self.actual_total_cost
    
    def calculate_remaining_amount(self):
        """حساب المبلغ المتبقي"""
        if self.actual_total_cost is None:
            return self.contract_total_cost - self.paid_amount
        return self.actual_total_cost - self.paid_amount
    
    def update_status(self, status):
        """تحديث حالة البند"""
        valid_statuses = ['نشط', 'مكتمل', 'متوقف']
        if status in valid_statuses:
            self.status = status
            return True
        return False