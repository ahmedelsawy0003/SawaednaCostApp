from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.extensions import db
from app.models.boq_item import BOQItem
from app.models.project import Project
# ✅ الإصلاح: تم إلغاء التعليق وضمان أن الدوال متاحة
from app.utils.excel_utils import export_boq_to_excel, import_boq_from_excel 
from datetime import datetime
from io import BytesIO

boq_bp = Blueprint('boq', __name__, url_prefix='/boq')


@boq_bp.route('/')
@login_required
def index():
    """List all BOQ items"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    query = BOQItem.query.order_by(BOQItem.item_number)
    
    # Filter by project
    project_id = request.args.get('project_id', type=int)
    if project_id:
        query = query.filter_by(project_id=project_id)
    
    # Filter by category
    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    projects = Project.query.all()
    
    # Calculate totals
    total_value = db.session.query(db.func.sum(BOQItem.total_value)).scalar() or 0
    executed_value = db.session.query(db.func.sum(BOQItem.executed_quantity * BOQItem.unit_price)).scalar() or 0
    remaining_value = total_value - executed_value
    
    return render_template('boq/index.html',
                         items=items,
                         pagination=pagination,
                         projects=projects,
                         total_value=total_value,
                         executed_value=executed_value,
                         remaining_value=remaining_value)


@boq_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new BOQ item"""
    if request.method == 'POST':
        try:
            boq_item = BOQItem(
                project_id=request.form.get('project_id'),
                item_number=request.form.get('item_number'),
                description=request.form.get('description'),
                unit=request.form.get('unit'),
                quantity=float(request.form.get('quantity')),
                unit_price=float(request.form.get('unit_price')),
                category=request.form.get('category'),
                notes=request.form.get('notes')
            )
            
            # حساب القيمة الإجمالية عند الإنشاء (مُضافة للإصلاح)
            boq_item.total_price = boq_item.quantity * boq_item.unit_price 
            
            db.session.add(boq_item)
            db.session.commit()
            
            flash('تم إضافة البند بنجاح', 'success')
            return redirect(url_for('boq.view', id=boq_item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    projects = Project.query.all()
    return render_template('boq/form.html',
                         projects=projects,
                         boq_item=None)


@boq_bp.route('/<int:id>')
@login_required
def view(id):
    """View BOQ item details"""
    boq_item = BOQItem.query.get_or_404(id)
    return render_template('boq/view.html',
                         boq_item=boq_item)


@boq_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit BOQ item"""
    boq_item = BOQItem.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            boq_item.project_id = request.form.get('project_id')
            boq_item.item_number = request.form.get('item_number')
            boq_item.description = request.form.get('description')
            boq_item.unit = request.form.get('unit')
            
            boq_item.quantity = float(request.form.get('quantity'))
            boq_item.unit_price = float(request.form.get('unit_price'))
            
            # تحديث القيمة الإجمالية عند التعديل (مُضافة للإصلاح)
            boq_item.total_price = boq_item.quantity * boq_item.unit_price
            
            boq_item.category = request.form.get('category')
            boq_item.notes = request.form.get('notes')
            
            db.session.commit()
            flash('تم تحديث البند بنجاح', 'success')
            return redirect(url_for('boq.view', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    projects = Project.query.all()
    return render_template('boq/form.html',
                         projects=projects,
                         boq_item=boq_item)


@boq_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete BOQ item"""
    boq_item = BOQItem.query.get_or_404(id)
    
    try:
        db.session.delete(boq_item)
        db.session.commit()
        flash('تم حذف البند بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return redirect(url_for('boq.index'))


@boq_bp.route('/<int:id>/update-execution', methods=['POST'])
@login_required
def update_execution(id):
    """Update execution quantity"""
    boq_item = BOQItem.query.get_or_404(id)
    
    try:
        executed_qty = float(request.form.get('executed_quantity'))
        boq_item.executed_quantity = executed_qty
        
        # تحديث نسبة الإنجاز عند التحديث (مُضافة للإصلاح)
        boq_item.update_completion_percentage()

        db.session.commit()
        flash('تم تحديث كمية التنفيذ بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return redirect(url_for('boq.view', id=id))


@boq_bp.route('/export/excel')
@login_required
def export_excel():
    """Export BOQ to Excel"""
    project_id = request.args.get('project_id', type=int)
    
    if project_id:
        items = BOQItem.query.filter_by(project_id=project_id).all()
        project = Project.query.get(project_id)
        filename = f'boq_{project.name}.xlsx'
    else:
        items = BOQItem.query.all()
        filename = 'boq_all.xlsx'
    
    output = export_boq_to_excel(items)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@boq_bp.route('/import/excel', methods=['GET', 'POST'])
@login_required
def import_excel():
    """Import BOQ from Excel"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('يجب أن يكون الملف بصيغة Excel', 'danger')
            return redirect(request.url)
        
        try:
            project_id = request.form.get('project_id', type=int)
            items_data = import_boq_from_excel(file)
            
            # Create BOQ items
            for item_data in items_data:
                # حساب القيمة الإجمالية أثناء الاستيراد (مُضافة للإصلاح)
                total_price = item_data.get('quantity', 0) * item_data.get('unit_price', 0)
                
                boq_item = BOQItem(
                    project_id=project_id,
                    total_price=total_price,
                    **item_data
                )
                db.session.add(boq_item)
            
            db.session.commit()
            flash(f'تم استيراد {len(items_data)} بند بنجاح', 'success')
            return redirect(url_for('boq.index', project_id=project_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ في الاستيراد: {str(e)}', 'danger')
    
    projects = Project.query.all()
    return render_template('boq/import.html', projects=projects)


@boq_bp.route('/download-template')
@login_required
def download_template():
    """Download empty BOQ template"""
    output = export_boq_to_excel([])
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='boq_template.xlsx'
    )