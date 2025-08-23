from app.extensions import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # <<< تم التعديل هنا: تم حذف الشرطة المائلة للخلف \
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True) # Can be linked to an item
    # <<< تم التعديل هنا: تم حذف الشرطة المائلة للخلف \
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False) # Or directly to a project
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    description = db.Column(db.Text)

    item = db.relationship('Item', backref=db.backref('payments', lazy=True))
    # project = db.relationship('Project', backref=db.backref('payments', lazy=True)) # This line is commented out to avoid conflict

    def __repr__(self):
        return f'<Payment {self.amount} for Project {self.project_id}>'