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

    def __init__(self, item, quantity):
        self.item = item
        self.description = f"{item.item_number} - {item.description}"
        self.quantity = quantity
        # Use actual_unit_cost if available, otherwise use contract_unit_cost
        self.unit_price = item.actual_unit_cost if item.actual_unit_cost is not None and item.actual_unit_cost > 0 else item.contract_unit_cost
        self.total_price = self.quantity * self.unit_price

    def __repr__(self):
        return f'<InvoiceItem for Item {self.item_id} on Invoice {self.invoice_id}>'