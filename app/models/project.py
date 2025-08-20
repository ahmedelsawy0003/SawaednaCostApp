from app.extensions import db
from datetime import datetime

class Project(db.Model):
    """نموذج المشروع"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    manager = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    spreadsheet_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('Item', backref='project', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total_contract_cost(self):
        """حساب إجمالي التكلفة التعاقدية كخاصية"""
        return sum(item.contract_total_cost for item in self.items if item.contract_total_cost)

    @property
    def total_actual_cost(self):
        """حساب إجمالي التكلفة الفعلية كخاصية"""
        return sum(item.actual_total_cost for item in self.items if item.actual_total_cost)

    @property
    def total_savings(self):
        """حساب إجمالي الوفر/الزيادة كخاصية"""
        return self.total_contract_cost - self.total_actual_cost

    @property
    def completion_percentage(self):
        """حساب نسبة الإنجاز كخاصية"""
        if not self.items:
            return 0
        
        completed_items_cost = sum(item.actual_total_cost or 0 for item in self.items if item.status == 'مكتمل')
        total_cost = self.total_contract_cost
        if total_cost == 0:
            return 0
            
        return (completed_items_cost / total_cost) * 100

    def to_dict(self):
        """تحويل المشروع إلى قاموس لواجهات API"""
        return {
            'id': self.id,
            'name': self.name,
            'manager': self.manager,
            'location': self.location,
            'spreadsheet_id': self.spreadsheet_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_contract_cost': self.total_contract_cost,
            'total_actual_cost': self.total_actual_cost,
            'total_savings': self.total_savings,
            'completion_percentage': self.completion_percentage
        }