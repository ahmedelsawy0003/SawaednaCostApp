from app.extensions import db
from sqlalchemy.orm import relationship


class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    notes = db.Column(db.Text, nullable=True)
    
    # <<< التعديل: تغيير lazy=True إلى lazy='dynamic'
    items = db.relationship('Item', back_populates='contractor', lazy='dynamic') 

    # --- بداية الإضافة ---
    # تعريف العلاقة المفقودة مع تفاصيل التكلفة
    # <<< التعديل: إضافة lazy='dynamic' لضمان كفاءة التعامل مع المستخلصات
    invoices = relationship('Invoice', back_populates='contractor', lazy='dynamic', cascade="all, delete-orphan")
    cost_details = db.relationship('CostDetail', back_populates='contractor', lazy='dynamic')
    # --- نهاية الإضافة ---

    def __repr__(self):
        return f'<Contractor {self.name}>'