from app.extensions import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    description = db.Column(db.Text)

    item = db.relationship('Item', backref=db.backref('payments', lazy=True, cascade="all, delete-orphan"))
    
    # This relationship defines the 'payments' attribute on the Project model
    project = db.relationship('Project', backref=db.backref('payments', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Payment {self.amount} for Project {self.project_id}>'