from app.extensions import db
from .user import user_project_association
from .invoice import Invoice
from .payment import Payment # <<< أضف هذا السطر

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    start_date = db.Column(db.String(10))
    end_date = db.Column(db.String(10))
    status = db.Column(db.String(50), default='قيد التنفيذ')
    notes = db.Column(db.Text)
    spreadsheet_id = db.Column(db.String(255))
    
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    users = db.relationship(
        'User', 
        secondary=user_project_association,
        back_populates='projects'
    )
    
    manager = db.relationship('User', foreign_keys=[manager_id])

    invoices = db.relationship('Invoice', back_populates='project', lazy='dynamic', cascade="all, delete-orphan")

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
        items_list = self.items 
        if not items_list:
            return 0.0
        if len(items_list) == 0:
            return 0.0
        completed_items = sum(1 for item in items_list if item.status == 'مكتمل')
        return (completed_items / len(items_list)) * 100

    @property
    def financial_completion_percentage(self):
        total_actual = self.total_actual_cost
        if total_actual == 0:
            return 0.0
        return (self.total_paid_amount / total_actual) * 100

    @property
    def total_paid_amount(self):
        # START: *** THE FIX ***
        # This is the correct way to calculate the sum across relationships.
        # It joins Invoice and Payment tables and sums the Payment.amount.
        total_paid = db.session.query(db.func.sum(Payment.amount)).join(Invoice).filter(Invoice.project_id == self.id).scalar()
        
        return total_paid or 0.0
        # END: *** THE FIX ***

    @property
    def total_remaining_amount(self):
        # This will now be correct because it depends on total_paid_amount
        return self.total_actual_cost - self.total_paid_amount

    def __repr__(self):
        return f'<Project {self.name}>'