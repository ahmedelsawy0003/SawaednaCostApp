from app.extensions import db

class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)

    # --- START: حذف العلاقة القديمة ---
    # تم حذف العلاقة cost_details
    # --- END: حذف العلاقة القديمة ---

    # This is the relationship for items where this contractor is the main one.
    items = db.relationship('Item', back_populates='contractor', lazy='dynamic')
    
    # This relationship is correct and should remain
    invoices = db.relationship('Invoice', back_populates='contractor', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Contractor {self.name}>'