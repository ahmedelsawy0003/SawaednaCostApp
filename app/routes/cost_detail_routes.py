from flask import Blueprint, request, redirect, url_for, flash, render_template
from app.models.item import Item
from app.models.cost_detail import CostDetail
from app.extensions import db
from flask_login import login_required
from app.utils import check_project_permission, sanitize_input

cost_detail_bp = Blueprint('cost_detail', __name__, url_prefix='/cost-details')

@cost_detail_bp.route('/item/<int:item_id>', methods=['POST'])
@login_required
def add_cost_detail(item_id):
    """إضافة تفصيل تكلفة جديد لبند معين"""
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)
    data = request.form

    try:
        description = sanitize_input(data.get('description'))
        unit = sanitize_input(data.get('unit'))
        quantity = float(data.get('quantity', 0))
        unit_cost = float(data.get('unit_cost', 0))
        total_cost = quantity * unit_cost

        new_detail = CostDetail(
            item_id=item.id,
            description=description,
            unit=unit,
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

# START: New Edit Function
@cost_detail_bp.route('/<int:detail_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cost_detail(detail_id):
    """تعديل تفصيل تكلفة موجود"""
    detail = CostDetail.query.get_or_404(detail_id)
    check_project_permission(detail.item.project)

    if request.method == 'POST':
        try:
            detail.description = sanitize_input(request.form.get('description'))
            detail.unit = sanitize_input(request.form.get('unit'))
            quantity = float(request.form.get('quantity', 0))
            unit_cost = float(request.form.get('unit_cost', 0))
            
            detail.quantity = quantity
            detail.unit_cost = unit_cost
            detail.total_cost = quantity * unit_cost
            
            db.session.commit()
            flash('تم تحديث تفصيل التكلفة بنجاح.', 'success')
            return redirect(url_for('item.edit_item', item_id=detail.item_id))
        except (ValueError, TypeError):
            flash('بيانات التحديث غير صالحة.', 'danger')
            return redirect(url_for('cost_detail.edit_cost_detail', detail_id=detail.id))

    return render_template('cost_details/edit.html', detail=detail)
# END: New Edit Function

@cost_detail_bp.route('/<int:detail_id>/delete', methods=['POST'])
@login_required
def delete_cost_detail(detail_id):
    """حذف تفصيل تكلفة"""
    detail = CostDetail.query.get_or_404(detail_id)
    check_project_permission(detail.item.project)
    item_id = detail.item_id

    db.session.delete(detail)
    db.session.commit()
    flash('تم حذف تفصيل التكلفة بنجاح', 'success')

    return redirect(url_for('item.edit_item', item_id=item_id))