from app.extensions import db

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    # This always links to the main project item for overall tracking
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False) 
    
    # --- START: الحقل الجديد لربط المستخلص بتفصيل تكلفة معين ---
    # This is optional and is used only when invoicing for a specific cost detail (subcontractor work)
    cost_detail_id = db.Column(db.Integer, db.ForeignKey('cost_detail.id'), nullable=True)
    # --- END: الحقل الجديد ---

    # Relationships
    invoice = db.relationship('Invoice', back_populates='items')
    item = db.relationship('Item', backref=db.backref('invoice_items', lazy=True))
    payments = db.relationship('Payment', back_populates='invoice_item', cascade="all, delete-orphan")
    
    # --- START: علاقة جديدة مع تفصيل التكلفة ---
    cost_detail = db.relationship('CostDetail', backref=db.backref('invoice_items', lazy=True))
    # --- END: علاقة جديدة ---

    def __init__(self, quantity, item=None, cost_detail=None):
        if item:
            # Case 1: This is for a main project item
            self.item = item
            self.description = f"{item.item_number} - {item.description}"
            actual_cost = item.actual_unit_cost
            contract_cost = item.contract_unit_cost
            self.unit_price = actual_cost if actual_cost is not None and actual_cost > 0 else (contract_cost or 0.0)

        elif cost_detail:
            # Case 2: This is for a subcontracted cost detail
            self.cost_detail = cost_detail
            self.item = cost_detail.item # Still link to the parent item
            self.description = f"تفصيل: {cost_detail.description}"
            self.unit_price = cost_detail.unit_cost or 0.0
        
        else:
            raise ValueError("InvoiceItem must be initialized with either an 'item' or a 'cost_detail'.")

        self.quantity = quantity
        self.total_price = (self.quantity or 0.0) * self.unit_price

    def __repr__(self):
        return f'<InvoiceItem for Item {self.item_id} on Invoice {self.invoice_id}>'