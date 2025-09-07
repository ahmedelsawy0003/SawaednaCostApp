from app.extensions import db
from sqlalchemy.orm import relationship

class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    # This line creates the reverse relationship from Contractor back to Invoice
    invoices = relationship('Invoice', back_populates='contractor')

    def __repr__(self):
        return f'<Contractor {self.name}>'

