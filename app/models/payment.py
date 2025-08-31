from app.extensions import db
from sqlalchemy import event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

    # --- START: الإصلاح الرئيسي ---
    # نجعله قابلاً ليكون فارغاً للتعامل مع الدفعات القديمة
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)
    # --- END: الإصلاح الرئيسي ---
    
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'), nullable=True)

    # Relationships
    invoice = db.relationship('Invoice', back_populates='payments')
    invoice_item = db.relationship('InvoiceItem', back_populates='payments')
    
    # --- START: إعادة العلاقات القديمة للقراءة فقط ---
    # سنعيد هذه الحقول حتى لا يتعطل أي جزء قديم من النظام تماماً
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    # --- END: إعادة العلاقات القديمة ---


    __table_args__ = (
        db.Index('idx_payment_invoice_id', 'invoice_id'),
        db.Index('idx_payment_invoice_item_id', 'invoice_item_id'),
    )

    def __repr__(self):
        return f'<Payment {self.amount} for Invoice {self.invoice_id}>'

@event.listens_for(Payment, 'after_insert')
@event.listens_for(Payment, 'after_update')
@event.listens_for(Payment, 'after_delete')
def receive_after_payment_change(mapper, connection, target):
    if target.invoice:
        target.invoice.update_status()

from .invoice_item import InvoiceItem