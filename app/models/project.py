from app.extensions import db
from .user import user_project_association
from .invoice import Invoice
from .payment import Payment
from app import constants
from sqlalchemy.ext.hybrid import hybrid_property
from .item import Item

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default=constants.PROJECT_STATUS_IN_PROGRESS)
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

    items = db.relationship('Item', back_populates='project', cascade="all, delete-orphan")
    invoices = db.relationship('Invoice', back_populates='project', lazy='dynamic', cascade="all, delete-orphan")

    @hybrid_property
    def total_actual_cost(self):
        return sum(item.actual_total_cost for item in self.items if item.actual_total_cost is not None)

    def __repr__(self):
        return f'<Project {self.name}>'