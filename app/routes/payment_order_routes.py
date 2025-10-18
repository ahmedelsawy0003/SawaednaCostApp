from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.extensions import db
from app.models.payment_order import PaymentOrder
from app.models.project import Project
from app.models.item import Item
from app.utils.sequence_utils import generate_payment_order_number
from app.utils.pdf_utils import generate_payment_order_pdf
from datetime import datetime

payment_orders_bp = Blueprint('payment_orders', __name__, url_prefix='/payment-orders')


@payment_orders_bp.route('/')
@login_required
def index():
    """List all payment orders"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = PaymentOrder.query.order_by(PaymentOrder.created_at.desc())
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # Filter by project
    project_id = request.args.get('project_id', type=int)
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    # Filter by payment type
    payment_type = request.args.get('payment_type')
    if payment_type:
        query = query.filter_by(payment_type=payment_type)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items
    
    projects = Project.query.all()
    
    # Calculate totals
    total_amount = db.session.query(db.func.sum(PaymentOrder.amount)).scalar() or 0
    pending_amount = db.session.query(db.func.sum(PaymentOrder.amount)).filter_by(status='pending').scalar() or 0
    paid_amount = db.session.query(db.func.sum(PaymentOrder.amount)).filter_by(status='paid').scalar() or 0
    
    return render_template('payment_orders/index.html',
                         orders=orders,
                         pagination=pagination,
                         projects=projects,
                         total_amount=total_amount,
                         pending_amount=pending_amount,
                         paid_amount=paid_amount)


@payment_orders_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new payment order"""
    if request.method == 'POST':
        try:
            # Generate unique number
            payment_number = generate_payment_order_number()
            
            # Create payment order
            payment_order = PaymentOrder(
                payment_number=payment_number,
                project_id=request.form.get('project_id'),
                boq_item_id=request.form.get('boq_item_id') or None,
                payment_type=request.form.get('payment_type'),
                beneficiary=request.form.get('beneficiary'),
                amount=float(request.form.get('amount')),
                payment_date=datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date(),
                requester_id=current_user.id,
                status='pending',
                description=request.form.get('description'),
                notes=request.form.get('notes')
            )
            
            db.session.add(payment_order)
            db.session.commit()
            
            flash('تم إنشاء أمر الصرف بنجاح', 'success')
            return redirect(url_for('payment_orders.view', id=payment_order.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    projects = Project.query.all()
    boq_items = Item.query.all()
    
    return render_template('payment_orders/form.html',
                         projects=projects,
                         boq_items=boq_items,
                         payment_order=None)


@payment_orders_bp.route('/<int:id>')
@login_required
def view(id):
    """View payment order details"""
    payment_order = PaymentOrder.query.get_or_404(id)
    return render_template('payment_orders/view.html',
                         payment_order=payment_order)


@payment_orders_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit payment order"""
    payment_order = PaymentOrder.query.get_or_404(id)
    
    # Only allow editing if pending
    if payment_order.status != 'pending':
        flash('لا يمكن تعديل أمر معتمد أو مدفوع', 'warning')
        return redirect(url_for('payment_orders.view', id=id))
    
    if request.method == 'POST':
        try:
            payment_order.project_id = request.form.get('project_id')
            payment_order.boq_item_id = request.form.get('boq_item_id') or None
            payment_order.payment_type = request.form.get('payment_type')
            payment_order.beneficiary = request.form.get('beneficiary')
            payment_order.amount = float(request.form.get('amount'))
            payment_order.payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
            payment_order.description = request.form.get('description')
            payment_order.notes = request.form.get('notes')
            
            db.session.commit()
            flash('تم تحديث أمر الصرف بنجاح', 'success')
            return redirect(url_for('payment_orders.view', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    projects = Project.query.all()
    boq_items = Item.query.all()
    
    return render_template('payment_orders/form.html',
                         projects=projects,
                         boq_items=boq_items,
                         payment_order=payment_order)


@payment_orders_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete payment order"""
    payment_order = PaymentOrder.query.get_or_404(id)
    
    # Only allow deleting if pending
    if payment_order.status != 'pending':
        flash('لا يمكن حذف أمر معتمد أو مدفوع', 'warning')
        return redirect(url_for('payment_orders.index'))
    
    try:
        db.session.delete(payment_order)
        db.session.commit()
        flash('تم حذف أمر الصرف بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return redirect(url_for('payment_orders.index'))


@payment_orders_bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    """Approve payment order"""
    payment_order = PaymentOrder.query.get_or_404(id)
    
    if payment_order.status != 'pending':
        flash('الأمر ليس قيد المراجعة', 'warning')
        return redirect(url_for('payment_orders.view', id=id))
    
    payment_order.status = 'approved'
    payment_order.approved_by_id = current_user.id
    payment_order.approved_at = datetime.utcnow()
    db.session.commit()
    
    flash('تم اعتماد أمر الصرف', 'success')
    return redirect(url_for('payment_orders.view', id=id))


@payment_orders_bp.route('/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    """Reject payment order"""
    payment_order = PaymentOrder.query.get_or_404(id)
    
    if payment_order.status != 'pending':
        flash('الأمر ليس قيد المراجعة', 'warning')
        return redirect(url_for('payment_orders.view', id=id))
    
    payment_order.status = 'rejected'
    payment_order.rejection_reason = request.form.get('rejection_reason')
    db.session.commit()
    
    flash('تم رفض أمر الصرف', 'warning')
    return redirect(url_for('payment_orders.view', id=id))


@payment_orders_bp.route('/<int:id>/pay', methods=['POST'])
@login_required
def pay(id):
    """Mark payment order as paid"""
    payment_order = PaymentOrder.query.get_or_404(id)
    
    if payment_order.status != 'approved':
        flash('يجب اعتماد الأمر أولاً', 'warning')
        return redirect(url_for('payment_orders.view', id=id))
    
    payment_order.status = 'paid'
    payment_order.paid_by_id = current_user.id
    payment_order.paid_at = datetime.utcnow()
    payment_order.payment_method = request.form.get('payment_method')
    payment_order.reference_number = request.form.get('reference_number')
    db.session.commit()
    
    flash('تم تسجيل الدفع بنجاح', 'success')
    return redirect(url_for('payment_orders.view', id=id))


@payment_orders_bp.route('/<int:id>/export/pdf')
@login_required
def export_pdf(id):
    """Export payment order to PDF"""
    payment_order = PaymentOrder.query.get_or_404(id)
    
    output = generate_payment_order_pdf(payment_order)
    
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'payment_order_{payment_order.payment_number}.pdf'
    )

