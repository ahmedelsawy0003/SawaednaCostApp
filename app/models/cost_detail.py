from app.extensions import db

class CostDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    
    # START: Add new fields to match the form
    description = db.Column(db.Text)
    unit = db.Column(db.String(50))
    quantity = db.Column(db.Float)
    unit_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    # END: Add new fields

    # Added cascade option for proper deletion
    item = db.relationship('Item', backref=db.backref('cost_details', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<CostDetail {self.description} - {self.total_cost}>'