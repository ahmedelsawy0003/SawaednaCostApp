from app.extensions import db
from sqlalchemy.orm import relationship

from .cost_detail import CostDetail

class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(255))
    phone_number = db.Column(db.String(50))
    email = db.Column(db.String(255))

    items = db.relationship('Item', back_populates='contractor', lazy=True)

    # --- بداية الإضافة ---
    # تعريف العلاقة المفقودة مع تفاصيل التكلفة
    cost_details = db.relationship('CostDetail', back_populates='contractor', lazy='dynamic')
    # --- نهاية الإضافة ---

    def __repr__(self):
        return f'<Contractor {self.name}>'

