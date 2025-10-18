from app.extensions import db
from datetime import datetime

class BOQItem(db.Model):
    """
    Model for Bill of Quantities Items (بنود جدول الكميات)
    """
    __tablename__ = 'boq_item'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    item_number = db.Column(db.String(50), nullable=False)  # رقم البند
    description = db.Column(db.Text, nullable=False)  # وصف البند
    unit = db.Column(db.String(50), nullable=False)  # الوحدة
    
    # Quantities
    quantity = db.Column(db.Float, nullable=False)  # الكمية المخططة
    executed_quantity = db.Column(db.Float, default=0)  # الكمية المنفذة
    
    # Prices
    unit_price = db.Column(db.Float, nullable=False)  # سعر الوحدة
    total_price = db.Column(db.Float, nullable=False)  # السعر الإجمالي
    
    # Execution tracking
    completion_percentage = db.Column(db.Float, default=0)  # نسبة الإنجاز
    
    # Category/Classification
    category = db.Column(db.String(100), nullable=True)  # تصنيف البند (خرسانة، حديد، إلخ)
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('boq_items', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<BOQItem {self.item_number}: {self.description[:30]}>'
    
    @property
    def remaining_quantity(self):
        """Calculate remaining quantity"""
        return self.quantity - self.executed_quantity
    
    @property
    def executed_value(self):
        """Calculate executed value"""
        return self.executed_quantity * self.unit_price
    
    @property
    def remaining_value(self):
        """Calculate remaining value"""
        return self.remaining_quantity * self.unit_price
    
    def update_completion_percentage(self):
        """Update completion percentage based on executed quantity"""
        if self.quantity > 0:
            self.completion_percentage = (self.executed_quantity / self.quantity) * 100
        else:
            self.completion_percentage = 0
        
        # Ensure it doesn't exceed 100%
        if self.completion_percentage > 100:
            self.completion_percentage = 100
    
    @property
    def status(self):
        """Get status based on completion percentage"""
        if self.completion_percentage == 0:
            return 'not_started'
        elif self.completion_percentage < 100:
            return 'in_progress'
        else:
            return 'completed'
    
    @property
    def status_arabic(self):
        """Get Arabic translation for status"""
        status_translations = {
            'not_started': 'لم يبدأ',
            'in_progress': 'قيد التنفيذ',
            'completed': 'مكتمل'
        }
        return status_translations.get(self.status, self.status)
    
    @property
    def status_badge_class(self):
        """Get Bootstrap badge class for status"""
        status_classes = {
            'not_started': 'secondary',
            'in_progress': 'warning',
            'completed': 'success'
        }
        return status_classes.get(self.status, 'secondary')

