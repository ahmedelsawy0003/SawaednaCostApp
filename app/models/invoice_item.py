from app.extensions import db

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False) # Link to the original project item

    # Relationships
    invoice = db.relationship('Invoice', back_populates='items')
    item = db.relationship('Item', backref=db.backref('invoice_items', lazy=True))

    payments = db.relationship('Payment', back_populates='invoice_item', cascade="all, delete-orphan")

    def __init__(self, item, quantity):
        self.item = item
        self.description = f"{item.item_number} - {item.description}"
        self.quantity = quantity
        
        # --- START: التعديل الرئيسي لإصلاح الخطأ ---
        # استخدام السعر الفعلي أولاً، ثم التعاقدي، وإذا كان كلاهما غير موجود، استخدم 0.0
        actual_cost = item.actual_unit_cost
        contract_cost = item.contract_unit_cost
        
        # نستخدم القيمة 0.0 كقيمة افتراضية آمنة
        self.unit_price = actual_cost if actual_cost is not None and actual_cost > 0 else (contract_cost or 0.0)
        
        self.total_price = (self.quantity or 0.0) * self.unit_price
        # --- END: التعديل الرئيسي ---

    def __repr__(self):
        return f'<InvoiceItem for Item {self.item_id} on Invoice {self.invoice_id}>'