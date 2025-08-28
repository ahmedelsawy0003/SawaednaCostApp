from app.extensions import db

class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)

    # Relationship to CostDetail (remains the same)
    cost_details = db.relationship('CostDetail', back_populates='contractor', lazy='dynamic')

    # START: New relationship to Item
    # This will allow us to see all main items assigned to a contractor
    items = db.relationship('Item', back_populates='contractor', lazy='dynamic')
    # END: New relationship

    def __repr__(self):
        return f'<Contractor {self.name}>'