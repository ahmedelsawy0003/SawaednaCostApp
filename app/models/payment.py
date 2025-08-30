from app.extensions import db
from sqlalchemy import event

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

    # --- START: التعديل الرئيسي ---
    # جعل invoice_id مطلوباً (غير فارغ)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    # --- END: التعديل الرئيسي ---

    # تم حذف الحقول القديمة: item_id, project_id, cost_detail_id

    # --- START: تعديل العلاقات ---
    # علاقة الدفع بالفاتورة فقط
    invoice = db.relationship('Invoice', back_populates='payments')
    # --- END: تعديل العلاقات ---


    __table_args__ = (
        # تم حذف الفهارس القديمة والإبقاء على فهرس الفاتورة فقط
        db.Index('idx_payment_invoice_id', 'invoice_id'),
    )

    def __repr__(self):
        return f'<Payment {self.amount} for Invoice {self.invoice_id}>'

# يبقى هذا الجزء كما هو لأنه مفيد لتحديث حالة الفاتورة تلقائياً
@event.listens_for(Payment, 'after_insert')
@event.listens_for(Payment, 'after_update')
@event.listens_for(Payment, 'after_delete')
def receive_after_payment_change(mapper, connection, target):
    """After a payment is saved or deleted, update the parent invoice's status."""
    if target.invoice:
        target.invoice.update_status()