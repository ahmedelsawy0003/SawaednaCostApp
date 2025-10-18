from app.extensions import db
from datetime import datetime

class PaymentOrder(db.Model):
    """
    Model for Payment Orders (أوامر الصرف)
    For contractors, temporary labor, purchases, and other expenses
    """
    __tablename__ = 'payment_order'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    boq_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)  # Optional
    
    payment_type = db.Column(db.String(50), nullable=False)
    # Payment types: contractor, labor, purchase, other
    
    beneficiary = db.Column(db.String(200), nullable=False)  # المستفيد
    amount = db.Column(db.Float, nullable=False)  # المبلغ
    
    payment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    status = db.Column(db.String(20), default='pending', nullable=False)
    # Status options: pending, approved, paid, rejected, cancelled
    
    description = db.Column(db.Text)  # وصف الصرف
    notes = db.Column(db.Text)
    
    # Approval workflow
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Payment details
    paid_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # cash, bank_transfer, check
    reference_number = db.Column(db.String(100), nullable=True)  # رقم المرجع (شيك، حوالة، إلخ)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('payment_orders', lazy='dynamic'))
    boq_item = db.relationship('Item', backref=db.backref('payment_orders', lazy='dynamic'))
    requester = db.relationship('User', foreign_keys=[requester_id], backref='submitted_payment_orders')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_payment_orders')
    paid_by = db.relationship('User', foreign_keys=[paid_by_id], backref='processed_payment_orders')
    
    def __repr__(self):
        return f'<PaymentOrder {self.payment_number}>'
    
    @property
    def status_badge_class(self):
        """Get Bootstrap badge class for status"""
        status_classes = {
            'pending': 'warning',
            'approved': 'info',
            'paid': 'success',
            'rejected': 'danger',
            'cancelled': 'dark'
        }
        return status_classes.get(self.status, 'secondary')
    
    @property
    def status_arabic(self):
        """Get Arabic translation for status"""
        status_translations = {
            'pending': 'قيد الانتظار',
            'approved': 'معتمد',
            'paid': 'مدفوع',
            'rejected': 'مرفوض',
            'cancelled': 'ملغي'
        }
        return status_translations.get(self.status, self.status)
    
    @property
    def payment_type_arabic(self):
        """Get Arabic translation for payment type"""
        type_translations = {
            'contractor': 'مقاول',
            'labor': 'عمالة مؤقتة',
            'purchase': 'مشتريات',
            'other': 'أخرى'
        }
        return type_translations.get(self.payment_type, self.payment_type)
    
    @property
    def payment_method_arabic(self):
        """Get Arabic translation for payment method"""
        if not self.payment_method:
            return '-'
        method_translations = {
            'cash': 'نقداً',
            'bank_transfer': 'حوالة بنكية',
            'check': 'شيك'
        }
        return method_translations.get(self.payment_method, self.payment_method)

