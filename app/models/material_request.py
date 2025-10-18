from app.extensions import db
from datetime import datetime

class MaterialRequest(db.Model):
    """
    Model for Material Supply Requests (طلبات توريد المواد)
    """
    __tablename__ = 'material_request'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    boq_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)  # Optional
    
    request_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
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
    project = db.relationship('Project', backref=db.backref('material_requests', lazy='dynamic'))
    boq_item = db.relationship('Item', backref=db.backref('material_requests', lazy='dynamic'))
    requester = db.relationship('User', foreign_keys=[requester_id], backref='submitted_material_requests')
    project_manager = db.relationship('User', foreign_keys=[project_manager_id], backref='managed_material_requests')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_material_requests')
    items = db.relationship('MaterialRequestItem', backref='request', cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f'<MaterialRequest {self.request_number}>'
    
    @property
    def total_items(self):
        """Get total number of items in this request"""
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


class MaterialRequestItem(db.Model):
    """
    Model for individual items in a Material Request
    """
    __tablename__ = 'material_request_item'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('material_request.id'), nullable=False)
    
    boq_item_number = db.Column(db.String(50), nullable=True)  # رقم البند من BOQ
    material_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(50), nullable=False)  # الوحدة (متر، كيلو، قطعة، إلخ)
    
    quantity_available = db.Column(db.Float, default=0)  # الكمية المتاحة
    quantity_requested = db.Column(db.Float, nullable=False)  # الكمية المطلوبة
    required_date = db.Column(db.Date, nullable=False)  # تاريخ التوريد المطلوب
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaterialRequestItem {self.material_name}>'

