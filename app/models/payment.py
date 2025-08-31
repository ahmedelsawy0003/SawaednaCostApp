from app.extensions import db
from sqlalchemy import event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)

    # --- START: الإضافة الجديدة ---
    # هذا الحقل اختياري، يسمح بربط الدفعة ببند معين داخل الفاتورة
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'), nullable=True)
    # --- END: الإضافة الجديدة ---

    # Relationships
    invoice = db.relationship('Invoice', back_populates='payments')
    
    # --- START: العلاقة الجديدة ---
    invoice_item = db.relationship('InvoiceItem', back_populates='payments')
    # --- END: العلاقة الجديدة ---


    __table_args__ = (
        db.Index('idx_payment_invoice_id', 'invoice_id'),
        # --- START: الفهرس الجديد ---
        db.Index('idx_payment_invoice_item_id', 'invoice_item_id'),
        # --- END: الفهرس الجديد ---
    )

    def __repr__(self):
        return f'<Payment {self.amount} for Invoice {self.invoice_id}>'

@event.listens_for(Payment, 'after_insert')
@event.listens_for(Payment, 'after_update')
@event.listens_for(Payment, 'after_delete')
def receive_after_payment_change(mapper, connection, target):
    """After a payment is saved or deleted, update the parent invoice's status."""
    if target.invoice:
        target.invoice.update_status()

# --- START: استيراد النموذج المرتبط ---
# نحتاج لاستيراده هنا لتجنب الأخطاء
from .invoice_item import InvoiceItem
# --- END: استيراد النموذج المرتبط ---