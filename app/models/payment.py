from app.extensions import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    description = db.Column(db.Text)

    # START: Modified Foreign Keys
    # Each payment now belongs to a specific cost_detail
    cost_detail_id = db.Column(db.Integer, db.ForeignKey('cost_detail.id'), nullable=True)
    # END: Modified Foreign Keys

    # These fields are now deprecated as we can get them through the cost_detail -> item -> project relationship
    # We will remove them in a later migration.
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

    # These relationships will also be removed later
    item = db.relationship('Item', backref=db.backref('payments', lazy=True, cascade="all, delete-orphan"))
    project = db.relationship('Project', backref=db.backref('payments', lazy=True, cascade="all, delete-orphan"))

    __table_args__ = (
        db.Index('idx_payment_project_id', 'project_id'),
        db.Index('idx_payment_item_id', 'item_id'),
        # START: New Index
        db.Index('idx_payment_cost_detail_id', 'cost_detail_id'),
        # END: New Index
    )

    def __repr__(self):
        return f'<Payment {self.amount} for Cost Detail {self.cost_detail_id}>'