from app.extensions import db

class CostDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(\'item.id\'), nullable=False)
    date = db.Column(db.String(10)) # YYYY-MM-DD
    description = db.Column(db.Text)
    amount = db.Column(db.Float)

    item = db.relationship(\'Item\', backref=db.backref(\'cost_details\', lazy=True))

    def __repr__(self):
        return f\' <CostDetail {self.description} - {self.amount}>\'


