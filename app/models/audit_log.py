from app.extensions import db
from sqlalchemy import func

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    action = db.Column(db.String(50), nullable=False)  # e.g., 'create', 'update'
    
    # To store changes as a simple text log
    details = db.Column(db.Text, nullable=False)

    user = db.relationship('User')
    item = db.relationship('Item', backref=db.backref('history_logs', lazy='dynamic', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<AuditLog {self.id} for Item {self.item_id}>'