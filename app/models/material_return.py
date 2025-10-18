from app.extensions import db
from datetime import datetime

class MaterialReturn(db.Model):
    """
    Model for Material Returns (مرتجعات المواد)
    """
    __tablename__ = 'material_return'
    
    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    boq_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)  # Optional
    
    return_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    status = db.Column(db.String(20), default='draft', nullable=False)
    # Status options: draft, pending, approved, rejected, completed, cancelled
    
    notes = db.Column(db.Text)
    
    # Approval workflow
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('material_returns', lazy='dynamic'))
    boq_item = db.relationship('Item', backref=db.backref('material_returns', lazy='dynamic'))
    requester = db.relationship('User', foreign_keys=[requester_id], backref='submitted_material_returns')
    project_manager = db.relationship('User', foreign_keys=[project_manager_id], backref='managed_material_returns')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_material_returns')
    items = db.relationship('MaterialReturnItem', backref='return_request', cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f'<MaterialReturn {self.return_number}>'
    
    @property
    def total_items(self):
        """Get total number of items in this return"""
        return self.items.count()
    
    @property
    def status_badge_class(self):
        """Get Bootstrap badge class for status"""
        status_classes = {
            'draft': 'secondary',
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'completed': 'primary',
            'cancelled': 'dark'
        }
        return status_classes.get(self.status, 'secondary')
    
    @property
    def status_arabic(self):
        """Get Arabic translation for status"""
        status_translations = {
            'draft': 'مسودة',
            'pending': 'قيد المراجعة',
            'approved': 'معتمد',
            'rejected': 'مرفوض',
            'completed': 'مكتمل',
            'cancelled': 'ملغي'
        }
        return status_translations.get(self.status, self.status)


class MaterialReturnItem(db.Model):
    """
    Model for individual items in a Material Return
    """
    __tablename__ = 'material_return_item'
    
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('material_return.id'), nullable=False)
    
    boq_item_number = db.Column(db.String(50), nullable=True)  # رقم البند من BOQ
    material_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(50), nullable=False)  # الوحدة (متر، كيلو، قطعة، إلخ)
    
    quantity = db.Column(db.Float, nullable=False)  # الكمية المرتجعة
    notes = db.Column(db.Text)  # ملاحظات عن البند
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaterialReturnItem {self.material_name}>'

