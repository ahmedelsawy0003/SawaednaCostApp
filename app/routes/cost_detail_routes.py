from flask import Blueprint, request, redirect, url_for, flash
from app.models.item import Item
from app.models.cost_detail import CostDetail
from app.extensions import db

cost_detail_bp = Blueprint('cost_detail', __name__, url_prefix='/cost-details')

@cost_detail_bp.route('/item/<int:item_id>', methods=['POST'])
def add_cost_detail(item_id):
    """إضافة تفصيل تكلفة جديد لبند معين"""
    item = Item.query.get_or_404(item_id)
    data = request.form

    try:
        quantity = float(data.get('quantity', 1))
        unit_cost = float(data.get('unit_cost', 0))
        total_cost = quantity * unit_cost

        new_detail = CostDetail(
            item_id=item.id,
            description=data.get('description'),
            unit=data.get('unit'),
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=total_cost
        )
        db.session.add(new_detail)
        db.session.commit()
        flash('تمت إضافة تفصيل التكلفة بنجاح', 'success')
    except (ValueError, TypeError):
        flash('بيانات غير صالحة. يرجى إدخال أرقام صحيحة للكمية والتكلفة.', 'danger')

    return redirect(url_for('item.edit_item', item_id=item_id))

@cost_detail_bp.route('/<int:detail_id>/delete', methods=['POST'])
def delete_cost_detail(detail_id):
    """حذف تفصيل تكلفة"""
    detail = CostDetail.query.get_or_404(detail_id)
    item_id = detail.item_id

    db.session.delete(detail)
    db.session.commit()
    flash('تم حذف تفصيل التكلفة بنجاح', 'success')

    return redirect(url_for('item.edit_item', item_id=item_id))