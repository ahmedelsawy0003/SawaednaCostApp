from app.extensions import db

class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)

    # This is the relationship for items where this contractor is the main one.
    items = db.relationship('Item', back_populates='contractor', lazy='dynamic')
    
    # This relationship is for invoices submitted by this contractor.
    invoices = db.relationship('Invoice', back_populates='contractor', lazy='dynamic')

    # --- START: العلاقة الجديدة مع تفاصيل التكاليف ---
    # This links the contractor to all the individual cost detail lines they are responsible for.
    cost_details = db.relationship('CostDetail', back_populates='contractor', lazy='dynamic')
    # --- END: العلاقة الجديدة ---

    def __repr__(self):
        return f'<Contractor {self.name}>'