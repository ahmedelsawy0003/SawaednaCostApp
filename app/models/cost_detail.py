from app.extensions import db

class CostDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    
    description = db.Column(db.Text)
    unit = db.Column(db.String(50))
    quantity = db.Column(db.Float)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    
    status = db.Column(db.String(50), nullable=False, server_default='غير مدفوع')

    item = db.relationship('Item', backref=db.backref('cost_details', lazy=True, cascade="all, delete-orphan"))

    # START: Add table arguments for indexing
    __table_args__ = (
        db.Index('idx_cost_detail_item_id', 'item_id'),
    )
    # END: Add table arguments

    def __repr__(self):
        return f'<CostDetail {self.description} - {self.total_cost}>'