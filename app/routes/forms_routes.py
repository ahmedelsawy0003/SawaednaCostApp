from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.material_request import MaterialRequest, MaterialRequestItem
from app.models.material_return import MaterialReturn, MaterialReturnItem
from app.models.project import Project
from app.models.item import Item
from app.utils.sequence_utils import generate_material_request_number, generate_material_return_number
from app.utils.excel_utils import (
    export_material_request_to_excel, export_material_return_to_excel,
    import_material_request_from_excel, import_material_return_from_excel,
    download_material_request_template, download_material_return_template
)
from app.utils.pdf_utils import generate_material_request_pdf, generate_material_return_pdf
from datetime import datetime

forms_bp = Blueprint('forms', __name__, url_prefix='/forms')


# ==================== Material Requests ====================

@forms_bp.route('/')
@login_required
def index():
    """Forms module home page"""
    material_requests_count = MaterialRequest.query.count()
    material_returns_count = MaterialReturn.query.count()
    
    return render_template('forms/index.html',
                         material_requests_count=material_requests_count,
                         material_returns_count=material_returns_count)


@forms_bp.route('/material-requests')
@login_required
def material_requests():
    """List all material requests"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = MaterialRequest.query.order_by(MaterialRequest.created_at.desc())
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # Filter by project
    project_id = request.args.get('project_id', type=int)
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    requests_list = pagination.items
    
    projects = Project.query.all()
    
    return render_template('forms/material_request_list.html',
                         requests=requests_list,
                         pagination=pagination,
                         projects=projects)


@forms_bp.route('/material-requests/new', methods=['GET', 'POST'])
@login_required
def new_material_request():
    """Create new material request"""
    if request.method == 'POST':
        try:
            # Generate unique number
            request_number = generate_material_request_number()
            
            # Create material request
            material_request = MaterialRequest(
                request_number=request_number,
                project_id=request.form.get('project_id'),
                boq_item_id=request.form.get('boq_item_id') or None,
                request_date=datetime.strptime(request.form.get('request_date'), '%Y-%m-%d').date(),
                requester_id=current_user.id,
                project_manager_id=request.form.get('project_manager_id') or None,
                status='draft',
                notes=request.form.get('notes')
            )
            
            db.session.add(material_request)
            db.session.flush()  # Get the ID
            
            # Add items
            item_count = int(request.form.get('item_count', 0))
            for i in range(item_count):
                item = MaterialRequestItem(
                    request_id=material_request.id,
                    boq_item_number=request.form.get(f'item_{i}_boq_number'),
                    material_name=request.form.get(f'item_{i}_name'),
                    description=request.form.get(f'item_{i}_description'),
                    unit=request.form.get(f'item_{i}_unit'),
                    quantity_available=float(request.form.get(f'item_{i}_available', 0) or 0),
                    quantity_requested=float(request.form.get(f'item_{i}_requested')),
                    required_date=datetime.strptime(request.form.get(f'item_{i}_required_date'), '%Y-%m-%d').date()
                )
                db.session.add(item)
            
            db.session.commit()
            flash('تم إنشاء طلب المواد بنجاح', 'success')
            return redirect(url_for('forms.material_requests'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    projects = Project.query.all()
    boq_items = Item.query.all()
    
    return render_template('forms/material_request_form.html',
                         projects=projects,
                         boq_items=boq_items,
                         material_request=None)


@forms_bp.route('/material-requests/<int:id>')
@login_required
def view_material_request(id):
    """View material request details"""
    material_request = MaterialRequest.query.get_or_404(id)
    return render_template('forms/material_request_view.html',
                         material_request=material_request)


@forms_bp.route('/material-requests/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material_request(id):
    """Edit material request"""
    material_request = MaterialRequest.query.get_or_404(id)
    
    # Only allow editing if draft
    if material_request.status != 'draft':
        flash('لا يمكن تعديل طلب معتمد أو قيد المراجعة', 'warning')
        return redirect(url_for('forms.view_material_request', id=id))
    
    if request.method == 'POST':
        try:
            material_request.project_id = request.form.get('project_id')
            material_request.boq_item_id = request.form.get('boq_item_id') or None
            material_request.request_date = datetime.strptime(request.form.get('request_date'), '%Y-%m-%d').date()
            material_request.project_manager_id = request.form.get('project_manager_id') or None
            material_request.notes = request.form.get('notes')
            
            # Delete existing items
            MaterialRequestItem.query.filter_by(request_id=material_request.id).delete()
            
            # Add new items
            item_count = int(request.form.get('item_count', 0))
            for i in range(item_count):
                item = MaterialRequestItem(
                    request_id=material_request.id,
                    boq_item_number=request.form.get(f'item_{i}_boq_number'),
                    material_name=request.form.get(f'item_{i}_name'),
                    description=request.form.get(f'item_{i}_description'),
                    unit=request.form.get(f'item_{i}_unit'),
                    quantity_available=float(request.form.get(f'item_{i}_available', 0) or 0),
                    quantity_requested=float(request.form.get(f'item_{i}_requested')),
                    required_date=datetime.strptime(request.form.get(f'item_{i}_required_date'), '%Y-%m-%d').date()
                )
                db.session.add(item)
            
            db.session.commit()
            flash('تم تحديث طلب المواد بنجاح', 'success')
            return redirect(url_for('forms.view_material_request', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    projects = Project.query.all()
    boq_items = Item.query.all()
    
    return render_template('forms/material_request_form.html',
                         projects=projects,
                         boq_items=boq_items,
                         material_request=material_request)


@forms_bp.route('/material-requests/<int:id>/delete', methods=['POST'])
@login_required
def delete_material_request(id):
    """Delete material request"""
    material_request = MaterialRequest.query.get_or_404(id)
    
    # Only allow deleting if draft
    if material_request.status != 'draft':
        flash('لا يمكن حذف طلب معتمد أو قيد المراجعة', 'warning')
        return redirect(url_for('forms.material_requests'))
    
    try:
        db.session.delete(material_request)
        db.session.commit()
        flash('تم حذف طلب المواد بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return redirect(url_for('forms.material_requests'))


@forms_bp.route('/material-requests/<int:id>/submit', methods=['POST'])
@login_required
def submit_material_request(id):
    """Submit material request for approval"""
    material_request = MaterialRequest.query.get_or_404(id)
    
    if material_request.status != 'draft':
        flash('الطلب مُرسل بالفعل', 'warning')
        return redirect(url_for('forms.view_material_request', id=id))
    
    material_request.status = 'pending'
    db.session.commit()
    
    flash('تم إرسال الطلب للمراجعة', 'success')
    return redirect(url_for('forms.view_material_request', id=id))


@forms_bp.route('/material-requests/<int:id>/approve', methods=['POST'])
@login_required
def approve_material_request(id):
    """Approve material request"""
    material_request = MaterialRequest.query.get_or_404(id)
    
    if material_request.status != 'pending':
        flash('الطلب ليس قيد المراجعة', 'warning')
        return redirect(url_for('forms.view_material_request', id=id))
    
    material_request.status = 'approved'
    material_request.approved_by_id = current_user.id
    material_request.approved_at = datetime.utcnow()
    db.session.commit()
    
    flash('تم اعتماد الطلب', 'success')
    return redirect(url_for('forms.view_material_request', id=id))


@forms_bp.route('/material-requests/<int:id>/reject', methods=['POST'])
@login_required
def reject_material_request(id):
    """Reject material request"""
    material_request = MaterialRequest.query.get_or_404(id)
    
    if material_request.status != 'pending':
        flash('الطلب ليس قيد المراجعة', 'warning')
        return redirect(url_for('forms.view_material_request', id=id))
    
    material_request.status = 'rejected'
    material_request.rejection_reason = request.form.get('rejection_reason')
    db.session.commit()
    
    flash('تم رفض الطلب', 'warning')
    return redirect(url_for('forms.view_material_request', id=id))


@forms_bp.route('/material-requests/<int:id>/export/excel')
@login_required
def export_material_request_excel(id):
    """Export material request to Excel"""
    material_request = MaterialRequest.query.get_or_404(id)
    
    output = export_material_request_to_excel(material_request)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'material_request_{material_request.request_number}.xlsx'
    )


@forms_bp.route('/material-requests/<int:id>/export/pdf')
@login_required
def export_material_request_pdf(id):
    """Export material request to PDF"""
    material_request = MaterialRequest.query.get_or_404(id)
    
    output = generate_material_request_pdf(material_request)
    
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'material_request_{material_request.request_number}.pdf'
    )


@forms_bp.route('/material-requests/templates/download')
@login_required
def download_material_request_template_route():
    """Download empty material request template"""
    output = download_material_request_template()
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='material_request_template.xlsx'
    )


@forms_bp.route('/material-requests/import', methods=['POST'])
@login_required
def import_material_request():
    """Import material request from Excel"""
    if 'file' not in request.files:
        return jsonify({'error': 'لم يتم رفع ملف'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    try:
        items = import_material_request_from_excel(file)
        return jsonify({'success': True, 'items': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Material Returns ====================

@forms_bp.route('/material-returns')
@login_required
def material_returns():
    """List all material returns"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = MaterialReturn.query.order_by(MaterialReturn.created_at.desc())
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # Filter by project
    project_id = request.args.get('project_id', type=int)
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    returns_list = pagination.items
    
    projects = Project.query.all()
    
    return render_template('forms/material_return_list.html',
                         returns=returns_list,
                         pagination=pagination,
                         projects=projects)


@forms_bp.route('/material-returns/new', methods=['GET', 'POST'])
@login_required
def new_material_return():
    """Create new material return"""
    if request.method == 'POST':
        try:
            # Generate unique number
            return_number = generate_material_return_number()
            
            # Create material return
            material_return = MaterialReturn(
                return_number=return_number,
                project_id=request.form.get('project_id'),
                boq_item_id=request.form.get('boq_item_id') or None,
                return_date=datetime.strptime(request.form.get('return_date'), '%Y-%m-%d').date(),
                requester_id=current_user.id,
                project_manager_id=request.form.get('project_manager_id') or None,
                status='draft',
                notes=request.form.get('notes')
            )
            
            db.session.add(material_return)
            db.session.flush()
            
            # Add items
            item_count = int(request.form.get('item_count', 0))
            for i in range(item_count):
                item = MaterialReturnItem(
                    return_id=material_return.id,
                    boq_item_number=request.form.get(f'item_{i}_boq_number'),
                    material_name=request.form.get(f'item_{i}_name'),
                    description=request.form.get(f'item_{i}_description'),
                    unit=request.form.get(f'item_{i}_unit'),
                    quantity=float(request.form.get(f'item_{i}_quantity')),
                    notes=request.form.get(f'item_{i}_notes')
                )
                db.session.add(item)
            
            db.session.commit()
            flash('تم إنشاء مرتجع المواد بنجاح', 'success')
            return redirect(url_for('forms.material_returns'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    projects = Project.query.all()
    boq_items = Item.query.all()
    
    return render_template('forms/material_return_form.html',
                         projects=projects,
                         boq_items=boq_items,
                         material_return=None)


@forms_bp.route('/material-returns/<int:id>')
@login_required
def view_material_return(id):
    """View material return details"""
    material_return = MaterialReturn.query.get_or_404(id)
    return render_template('forms/material_return_view.html',
                         material_return=material_return)


@forms_bp.route('/material-returns/<int:id>/export/excel')
@login_required
def export_material_return_excel(id):
    """Export material return to Excel"""
    material_return = MaterialReturn.query.get_or_404(id)
    
    output = export_material_return_to_excel(material_return)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'material_return_{material_return.return_number}.xlsx'
    )


@forms_bp.route('/material-returns/<int:id>/export/pdf')
@login_required
def export_material_return_pdf(id):
    """Export material return to PDF"""
    material_return = MaterialReturn.query.get_or_404(id)
    
    output = generate_material_return_pdf(material_return)
    
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'material_return_{material_return.return_number}.pdf'
    )


@forms_bp.route('/material-returns/templates/download')
@login_required
def download_material_return_template_route():
    """Download empty material return template"""
    output = download_material_return_template()
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='material_return_template.xlsx'
    )

