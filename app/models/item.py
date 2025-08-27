from app.extensions import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    item_number = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50))
    contract_quantity = db.Column(db.Float)
    contract_unit_cost = db.Column(db.Float)
    actual_quantity = db.Column(db.Float)
    actual_unit_cost = db.Column(db.Float)
    status = db.Column(db.String(50), default='نشط')
    execution_method = db.Column(db.String(100))
    contractor = db.Column(db.String(255))
    notes = db.Column(db.Text)

    project = db.relationship('Project', backref=db.backref('items', lazy=True, cascade="all, delete-orphan"))

    __table_args__ = (
        db.Index('idx_item_project_id', 'project_id'),
    )

    @property
    def paid_amount(self):
        """Calculates the total paid amount by summing up associated payments."""
        if not self.payments:
            return 0.0
        return sum(payment.amount for payment in self.payments)
    
    @property
    def contract_total_cost(self):
        if self.contract_quantity is not None and self.contract_unit_cost is not None:
            return self.contract_quantity * self.contract_unit_cost
        return 0.0

    @property
    def actual_total_cost(self):
        if self.actual_quantity is not None and self.actual_unit_cost is not None:
            return self.actual_quantity * self.actual_unit_cost
        return 0.0

    @property
    def cost_variance(self):
        return self.contract_total_cost - self.actual_total_cost

    @property
    def quantity_variance(self):
        if self.actual_quantity is not None:
            return self.contract_quantity - self.actual_quantity
        return self.contract_quantity

    @property
    def remaining_amount(self):
        return self.actual_total_cost - self.paid_amount
        
    # START: New property for a shorter, display-friendly description
    @property
    def short_description(self):
        """Returns a truncated version of the description for display purposes."""
        if len(self.description) > 50:
            return self.description[:50] + '...'
        return self.description
    # END: New property

    def __repr__(self):
        return f'<Item {self.item_number} - {self.description}>'