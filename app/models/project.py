from app.extensions import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    start_date = db.Column(db.String(10)) # YYYY-MM-DD
    end_date = db.Column(db.String(10))   # YYYY-MM-DD
    status = db.Column(db.String(50), default='قيد التنفيذ')
    notes = db.Column(db.Text)
    spreadsheet_id = db.Column(db.String(255)) # Google Sheets ID

    # Relationships
    items = db.relationship(\'Item\', backref=\'project\', lazy=True, cascade=\'all, delete-orphan\')
    payments = db.relationship(\'Payment\', backref=\'project\', lazy=True, cascade=\'all, delete-orphan\')

    @property
    def total_contract_cost(self):
        return sum(item.contract_total_cost for item in self.items)

    @property
    def total_actual_cost(self):
        return sum(item.actual_total_cost for item in self.items if item.actual_total_cost is not None)

    @property
    def total_savings(self):
        return self.total_contract_cost - self.total_actual_cost

    @property
    def completion_percentage(self):
        total_items = len(self.items)
        if total_items == 0:
            return 0
        completed_items = sum(1 for item in self.items if item.status == \'مكتمل\')
        return (completed_items / total_items) * 100

    @property
    def financial_completion_percentage(self):
        if self.total_contract_cost == 0:
            return 0
        return (self.total_actual_cost / self.total_contract_cost) * 100

    @property
    def total_paid_amount(self):
        return sum(payment.amount for payment in self.payments)

    @property
    def total_remaining_amount(self):
        return self.total_actual_cost - self.total_paid_amount

    def __repr__(self):
        return f\' <Project {self.name}>\'


