from app.extensions import db
from sqlalchemy import func

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    action = db.Column(db.String(50), nullable=False)  # e.g., 'create', 'update'
    
    details = db.Column(db.Text, nullable=False)

    user = db.relationship('User')
    item = db.relationship('Item', backref=db.backref('history_logs', lazy='dynamic', cascade="all, delete-orphan"))

    # START: Add table arguments for indexing
    __table_args__ = (
        db.Index('idx_audit_log_item_id', 'item_id'),
        db.Index('idx_audit_log_user_id', 'user_id'),
    )
    # END: Add table arguments

    def __repr__(self):
        return f'<AuditLog {self.id} for Item {self.item_id}>'