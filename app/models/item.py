from app.extensions import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # <<< تم التعديل هنا: تم حذف الشرطة المائلة للخلف \
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    item_number = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50))
    contract_quantity = db.Column(db.Float)
    contract_unit_cost = db.Column(db.Float)
    actual_quantity = db.Column(db.Float)
    actual_unit_cost = db.Column(db.Float)
    status = db.Column(db.String(50), default='نشط') # نشط, مكتمل, معلق
    execution_method = db.Column(db.String(100)) # مقاولة, توريد, عمالة, ذاتي
    contractor = db.Column(db.String(255))
    paid_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    project = db.relationship('Project', backref=db.backref('items', lazy=True))

    @property
    def contract_total_cost(self):
        return self.contract_quantity * self.contract_unit_cost

    @property
    def actual_total_cost(self):
        if self.actual_quantity is not None and self.actual_unit_cost is not None:
            return self.actual_quantity * self.actual_unit_cost
        return 0.0

    @property
    def cost_variance(self):
        return self.contract_total_cost - self.actual_total_cost

    @property
    def quantity_variance(self):
        if self.actual_quantity is not None:
            return self.contract_quantity - self.actual_quantity
        return self.contract_quantity

    @property
    def remaining_amount(self):
        return self.actual_total_cost - self.paid_amount

    def __repr__(self):
        return f'<Item {self.item_number} - {self.description}>'