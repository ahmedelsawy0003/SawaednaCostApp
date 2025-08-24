from app.extensions import db
# START: Import the new association table
from .user import user_project_association
# END: Import

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    start_date = db.Column(db.String(10))
    end_date = db.Column(db.String(10))
    status = db.Column(db.String(50), default='قيد التنفيذ')
    notes = db.Column(db.Text)
    spreadsheet_id = db.Column(db.String(255))
    
    # This defines the relationship back to the User model
    users = db.relationship(
        'User', 
        secondary=user_project_association,
        back_populates='projects'
    )

    @property
    def total_contract_cost(self):
        if not self.items:
            return 0.0
        return sum(item.contract_total_cost for item in self.items)

    @property
    def total_actual_cost(self):
        if not self.items:
            return 0.0
        return sum(item.actual_total_cost for item in self.items if item.actual_total_cost is not None)

    @property
    def total_savings(self):
        return self.total_contract_cost - self.total_actual_cost

    @property
    def completion_percentage(self):
        if not self.items:
            return 0.0
        completed_items = sum(1 for item in self.items if item.status == 'مكتمل')
        return (completed_items / len(self.items)) * 100

    @property
    def financial_completion_percentage(self):
        if self.total_contract_cost == 0:
            return 0.0
        return (self.total_paid_amount / self.total_contract_cost) * 100

    @property
    def total_paid_amount(self):
        if not self.payments:
            return 0.0
        return sum(payment.amount for payment in self.payments)

    @property
    def total_remaining_amount(self):
        return self.total_actual_cost - self.total_paid_amount

    def __repr__(self):
        return f'<Project {self.name}>'