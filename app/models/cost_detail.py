from app.extensions import db
from sqlalchemy import func

class CostDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50))
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    
    # --- START: الحقول الجديدة ---
    purchase_order_number = db.Column(db.String(100), nullable=True)
    disbursement_order_number = db.Column(db.String(100), nullable=True)
    # --- END: الحقول الجديدة ---

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=True)

    item = db.relationship('Item', back_populates='cost_details')
    contractor = db.relationship('Contractor', back_populates='cost_details')

    __table_args__ = (
        db.Index('idx_cost_detail_item_id', 'item_id'),
        db.Index('idx_cost_detail_contractor_id', 'contractor_id'),
    )

    @property
    def total_cost(self):
        if self.quantity is not None and self.unit_cost is not None:
            return self.quantity * self.unit_cost
        return 0.0

    def __repr__(self):
        return f'<CostDetail {self.description} for Item {self.item_id}>'