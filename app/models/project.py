from app.extensions import db
<<<<<<< HEAD
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
        return sum(item.actual_total_cost for item in self.items)

    @property
    def total_actual_quantity(self):
        """حساب إجمالي الكمية الفعلية من تفاصيل التكلفة"""
        total_qty = 0
        for item in self.items:
            total_qty += sum(detail.quantity for detail in item.cost_details if detail.quantity is not None)
        return total_qty

    @property
    def total_paid_amount(self):
        """حساب إجمالي المبلغ المدفوع لكل البنود"""
        return sum(item.paid_amount for item in self.items if item.paid_amount is not None)

    @property
    def total_remaining_amount(self):
        """(جديد) حساب إجمالي المبلغ المتبقي للمشروع"""
        return self.total_actual_cost - self.total_paid_amount

    @property
    def total_savings(self):
        """حساب إجمالي الوفر/الزيادة (الربح) كخاصية"""
=======

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    start_date = db.Column(db.String(10)) # YYYY-MM-DD
    end_date = db.Column(db.String(10))   # YYYY-MM-DD
    status = db.Column(db.String(50), default=\'قيد التنفيذ\')
    notes = db.Column(db.Text)
    spreadsheet_id = db.Column(db.String(255)) # Google Sheets ID

    # Relationships
    items = db.relationship(\'Item\', backref=\'project\', lazy=True, cascade=\'all, delete-orphan\')
    payments = db.relationship(\'Payment\', backref=\'project\', lazy=True, cascade=\'all, delete-orphan\')

    @property
    def total_contract_cost(self):
        return sum(item.contract_total_cost for item in self.items)

    @property
    def total_actual_cost(self):
        return sum(item.actual_total_cost for item in self.items if item.actual_total_cost is not None)

    @property
    def total_savings(self):
>>>>>>> 7a3713e (Initial commit with updated files)
        return self.total_contract_cost - self.total_actual_cost

    @property
    def completion_percentage(self):
<<<<<<< HEAD
        """حساب نسبة الإنجاز بناءً على عدد البنود"""
        if not self.items:
            return 0
        
        completed_count = sum(1 for item in self.items if item.status == 'مكتمل')
        total_count = len(self.items)
        
        return (completed_count / total_count) * 100

    @property
    def financial_completion_percentage(self):
        """حساب نسبة الإنجاز المالي بناءً على المدفوع مقابل الفعلي"""
        if self.total_actual_cost == 0:
            return 0
        
        percentage = (self.total_paid_amount / self.total_actual_cost) * 100
        return min(percentage, 100)

    def to_dict(self):
        """تحويل المشروع إلى قاموس لواجهات API (مُحدّث ليشمل كل الخصائص)"""
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
            'total_actual_quantity': self.total_actual_quantity,
            'total_paid_amount': self.total_paid_amount,
            'total_remaining_amount': self.total_remaining_amount, # تمت إضافة هذا السطر
            'total_savings': self.total_savings,
            'completion_percentage': self.completion_percentage,
            'financial_completion_percentage': self.financial_completion_percentage
        }
=======
        total_items = len(self.items)
        if total_items == 0:
            return 0
        completed_items = sum(1 for item in self.items if item.status == \'مكتمل\')
        return (completed_items / total_items) * 100

    @property
    def financial_completion_percentage(self):
        if self.total_contract_cost == 0:
            return 0
        return (self.total_actual_cost / self.total_contract_cost) * 100

    @property
    def total_paid_amount(self):
        return sum(payment.amount for payment in self.payments)

    @property
    def total_remaining_amount(self):
        return self.total_actual_cost - self.total_paid_amount

    def __repr__(self):
        return f\' <Project {self.name}>\'


>>>>>>> 7a3713e (Initial commit with updated files)
