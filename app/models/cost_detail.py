from app.extensions import db
from datetime import datetime

class CostDetail(db.Model):
    """نموذج لتفاصيل تكلفة البند (التكاليف النثرية)"""

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    description = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CostDetail {self.description}>'

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'description': self.description,
            'unit': self.unit,
            'quantity': self.quantity,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }