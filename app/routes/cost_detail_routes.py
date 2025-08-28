from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify
from app.models.item import Item
from app.models.cost_detail import CostDetail
from app.models.contractor import Contractor # <<< أضف هذا
from app.models.payment import Payment       # <<< أضف هذا
from app.extensions import db
from flask_login import login_required
from app.utils import check_project_permission, sanitize_input

cost_detail_bp = Blueprint('cost_detail', __name__, url_prefix='/cost-details')

@cost_detail_bp.route('/item/<int:item_id>', methods=['POST'])
@login_required
def add_cost_detail(item_id):
    """إضافة تفصيل تكلفة جديد وربطه بالمقاول والدفعات"""
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
            total_cost=total_cost,
            purchase_order=sanitize_input(data.get('purchase_order')),
            payment_order=sanitize_input(data.get('payment_order')),
            payment_method=data.get('payment_method', 'دفعة واحدة'),
            contractor_id=int(data.get('contractor_id')) if data.get('contractor_id') else None
        )
        db.session.add(new_detail)
        db.session.flush() # Flush to get the new_detail.id for the payment

        # إذا كانت طريقة الدفع "دفعة واحدة", أنشئ دفعة تلقائية بكامل المبلغ
        if new_detail.payment_method == 'دفعة واحدة':
            initial_payment = Payment(
                amount=total_cost,
                payment_date=data.get('payment_date'), # سنضيف حقل التاريخ في الواجهة
                description="دفعة تلقائية لكامل المبلغ",
                cost_detail_id=new_detail.id
            )
            db.session.add(initial_payment)

        db.session.commit()
        flash('تمت إضافة تفصيل التكلفة بنجاح.', 'success')
    except (ValueError, TypeError) as e:
        db.session.rollback()
        flash(f'بيانات غير صالحة. يرجى التحقق من المدخلات: {e}', 'danger')

    return redirect(url_for('item.edit_item', item_id=item_id))


@cost_detail_bp.route('/<int:detail_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cost_detail(detail_id):
    """تعديل تفصيل تكلفة موجود"""
    detail = CostDetail.query.get_or_404(detail_id)
    check_project_permission(detail.item.project)
    
    # سنحتاج قائمة المقاولين هنا لعرضها في نموذج التعديل
    contractors = Contractor.query.order_by(Contractor.name).all()

    if request.method == 'POST':
        try:
            detail.description = sanitize_input(request.form.get('description'))
            detail.unit = sanitize_input(request.form.get('unit'))
            quantity = float(request.form.get('quantity', 0))
            unit_cost = float(request.form.get('unit_cost', 0))
            
            detail.quantity = quantity
            detail.unit_cost = unit_cost
            detail.total_cost = quantity * unit_cost
            
            detail.purchase_order = sanitize_input(request.form.get('purchase_order'))
            detail.payment_order = sanitize_input(request.form.get('payment_order'))
            detail.contractor_id = int(request.form.get('contractor_id')) if request.form.get('contractor_id') else None

            db.session.commit()
            flash('تم تحديث تفصيل التكلفة بنجاح.', 'success')
            return redirect(url_for('item.edit_item', item_id=detail.item_id))
        except (ValueError, TypeError):
            flash('بيانات التحديث غير صالحة.', 'danger')
            return redirect(url_for('cost_detail.edit_cost_detail', detail_id=detail.id))

    return render_template('cost_details/edit.html', detail=detail, contractors=contractors)


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

# START: New route to add a payment (installment)
@cost_detail_bp.route('/<int:detail_id>/add_payment', methods=['POST'])
@login_required
def add_payment(detail_id):
    """إضافة دفعة (قسط) لتفصيل تكلفة معين"""
    detail = CostDetail.query.get_or_404(detail_id)
    check_project_permission(detail.item.project)
    
    try:
        amount = float(request.form.get('amount'))
        payment_date = request.form.get('payment_date')
        description = sanitize_input(request.form.get('description', ''))
        
        if not payment_date:
            flash('تاريخ الدفعة مطلوب.', 'danger')
            return redirect(url_for('item.edit_item', item_id=detail.item_id))

        new_payment = Payment(
            amount=amount,
            payment_date=payment_date,
            description=description,
            cost_detail_id=detail.id
        )
        db.session.add(new_payment)
        db.session.commit()
        flash('تمت إضافة الدفعة بنجاح.', 'success')
    except (ValueError, TypeError):
        flash('مبلغ الدفعة غير صالح.', 'danger')

    return redirect(url_for('item.edit_item', item_id=detail.item_id))
# END: New route

# START: New API route to add a contractor dynamically
@cost_detail_bp.route('/api/contractors/new', methods=['POST'])
@login_required
def api_add_contractor():
    """إضافة مقاول جديد من خلال API لاستخدامه في الواجهة الديناميكية"""
    data = request.json
    name = sanitize_input(data.get('name'))

    if not name:
        return jsonify({'success': False, 'message': 'اسم المقاول مطلوب'}), 400

    if Contractor.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': 'هذا المقاول موجود بالفعل'}), 409

    new_contractor = Contractor(name=name)
    db.session.add(new_contractor)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'تمت إضافة المقاول بنجاح',
        'contractor': {
            'id': new_contractor.id,
            'name': new_contractor.name
        }
    }), 201
# END: New API route