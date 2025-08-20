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
    
    # العلاقة مع بنود المشروع
    items = db.relationship('Item', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self):
        """تحويل المشروع إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'manager': self.manager,
            'location': self.location,
            'spreadsheet_id': self.spreadsheet_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_contract_cost': self.get_total_contract_cost(),
            'total_actual_cost': self.get_total_actual_cost(),
            'total_savings': self.get_total_savings(),
            'completion_percentage': self.get_completion_percentage()
        }
    
    def get_total_contract_cost(self):
        """حساب إجمالي التكلفة التعاقدية"""
        return sum(item.contract_total_cost for item in self.items if item.contract_total_cost)
    
    def get_total_actual_cost(self):
        """حساب إجمالي التكلفة الفعلية"""
        return sum(item.actual_total_cost for item in self.items if item.actual_total_cost)
    
    def get_total_savings(self):
        """حساب إجمالي الوفر/الزيادة"""
        return self.get_total_contract_cost() - self.get_total_actual_cost()
    
    def get_completion_percentage(self):
        """حساب نسبة الإنجاز"""
        if not self.items or self.get_total_contract_cost() == 0:
            return 0
        
        completed_items = sum(1 for item in self.items if item.status == 'مكتمل')
        return (completed_items / len(self.items)) * 100