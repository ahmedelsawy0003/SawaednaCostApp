from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import cast, Integer
from app.models.item import Item
from app.models.project import Project
from app.models.audit_log import AuditLog
from app.models.contractor import Contractor
from app.models.cost_detail import CostDetail 
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input
from app.forms import ItemForm

item_bp = Blueprint("item", __name__)

def log_item_change(item, action, changes_details=""):
    details = ""
    if action == 'create':
        details = f"تم إنشاء البند '{item.item_number}'."
    elif action == 'update':
        if changes_details:
            details = f"تم تحديث البند '{item.item_number}':\n{changes_details}"
        else:
            return 
    if not details:
        return

    log_entry = AuditLog(
        item_id=item.id,
        user_id=current_user.id,
        action=action,
        details=details
    )
    db.session.add(log_entry)

@item_bp.route("/projects/<int:project_id>/items")
@login_required
def get_items_by_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)

    search_query = request.args.get('search', '')
    query = Item.query.filter_by(project_id=project_id)

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Item.item_number.ilike(search_term)) |
            (Item.description.ilike(search_term))
        )

    items = query.order_by(Item.item_number).all()
    return render_template("items/index.html", items=items, project=project, search_query=search_query)

@item_bp.route("/projects/<int:project_id>/items/bulk_add", methods=['GET', 'POST'])
@login_required
def bulk_add_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project, require_admin=True)

    if request.method == 'POST':
        items_data = request.form.get('items_data')
        if not items_data:
            flash('لا توجد بيانات لإضافتها.', 'warning')
            return redirect(url_for('item.bulk_add_items', project_id=project_id))

        lines = items_data.strip().split('\n')
        added_count = 0
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                try:
                    item = Item(
                        project_id=project_id,
                        item_number=sanitize_input(parts[0]),
                        description=sanitize_input(parts[1]),
                        unit=sanitize_input(parts[2]),
                        contract_quantity=float(parts[3]),
                        contract_unit_cost=float(parts[4]),
                        status='نشط'
                    )
                    db.session.add(item)
                    added_count += 1
                except (ValueError, IndexError) as e:
                    flash(f'خطأ في تحليل السطر: {line}. تأكد من أن الكمية والسعر أرقام.', 'danger')
                    continue
        
        if added_count > 0:
            db.session.commit()
            flash(f'تمت إضافة {added_count} بندًا بنجاح.', 'success')
        
        return redirect(url_for('item.get_items_by_project', project_id=project_id))

    return render_template('items/bulk_add.html', project=project)

@item_bp.route('/projects/<int:project_id>/items/bulk_update', methods=['GET', 'POST'])
@login_required
def bulk_update_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project, require_admin=True)

    if request.method == 'POST':
        items_data = request.form.get('items_data_update')
        if not items_data:
            flash('لا توجد بيانات لتحديثها.', 'warning')
            return redirect(url_for('item.bulk_update_items', project_id=project_id))

        lines = items_data.strip().split('\n')
        updated_count = 0
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                item_number = sanitize_input(parts[0])
                item = Item.query.filter_by(project_id=project_id, item_number=item_number).first()
                if item:
                    try:
                        item.actual_quantity = float(parts[1]) if parts[1] else item.actual_quantity
                        item.actual_unit_cost = float(parts[2]) if parts[2] else item.actual_unit_cost
                        updated_count += 1
                    except (ValueError, IndexError):
                        flash(f'بيانات غير صالحة للكمية الفعلية أو تكلفة الوحدة الفعلية للبند {item_number}.', 'danger')
                        continue
        
        if updated_count > 0:
            db.session.commit()
            flash(f'تم تحديث {updated_count} بندًا بنجاح.', 'success')

        return redirect(url_for('item.get_items_by_project', project_id=project_id))
    
    items = Item.query.filter_by(project_id=project_id).order_by(Item.item_number).all()
    return render_template('items/bulk_update.html', project=project, items=items)

@item_bp.route("/projects/<int:project_id>/items/new", methods=["GET", "POST"])
@login_required
def new_item(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    
    form = ItemForm()
    
    contractors = Contractor.query.order_by(Contractor.name).all()
    form.contractor_id.choices = [(c.id, c.name) for c in contractors]
    form.contractor_id.choices.insert(0, (0, '-- اختر مقاولًا --'))

    if form.validate_on_submit():
        new_item = Item(project_id=project_id)
        form.populate_obj(new_item)
        
        if form.contractor_id.data == 0:
            new_item.contractor_id = None

        db.session.add(new_item)
        db.session.commit()
        
        log_item_change(new_item, 'create')
        db.session.commit()
        
        flash("تمت إضافة البند بنجاح.", "success")
        return redirect(url_for("item.get_items_by_project", project_id=project_id))
        
    return render_template("items/new.html", form=form, project=project, contractors=contractors)

# --- START: تحديث دالة edit_item ---
@item_bp.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    project = item.project
    check_project_permission(project)
    
    form = ItemForm(obj=item)
    form.contractor_id.choices = [(c.id, c.name) for c in Contractor.query.order_by(Contractor.name).all()]
    form.contractor_id.choices.insert(0, (0, '-- اختر مقاولًا --'))
    
    original_values = {
        'item_number': item.item_number, 'description': item.description, 'unit': item.unit,
        'contract_quantity': item.contract_quantity, 'contract_unit_cost': item.contract_unit_cost,
        'actual_quantity': item.actual_quantity, 'actual_unit_cost': item.actual_unit_cost,
        'status': item.status, 'notes': item.notes,
        'purchase_order_number': item.purchase_order_number,
        'disbursement_order_number': item.disbursement_order_number,
        'contractor_id': item.contractor_id
    }
    
    if form.validate_on_submit():
        changes_list = []
        field_map = {
            'item_number': 'رقم البند', 'description': 'الوصف', 'unit': 'الوحدة',
            'contract_quantity': 'الكمية التعاقدية', 'contract_unit_cost': 'تكلفة الوحدة التعاقدية',
            'actual_quantity': 'الكمية الفعلية', 'actual_unit_cost': 'تكلفة الوحدة الفعلية',
            'status': 'الحالة', 'notes': 'ملاحظات',
            'purchase_order_number': 'رقم أمر الشراء',
            'disbursement_order_number': 'رقم أمر الصرف',
            'contractor_id': 'المقاول'
        }

        new_contractor_id = form.contractor_id.data if form.contractor_id.data != 0 else None

        for field, label in field_map.items():
            old_value = original_values[field]
            if field == 'contractor_id':
                new_value = new_contractor_id
            else:
                new_value = getattr(form, field).data
            
            if old_value != new_value:
                if field == 'contractor_id':
                    old_contractor = Contractor.query.get(old_value) if old_value else None
                    new_contractor = Contractor.query.get(new_value) if new_value else None
                    old_display = old_contractor.name if old_contractor else 'لا شيء'
                    new_display = new_contractor.name if new_contractor else 'لا شيء'
                    changes_list.append(f"{label}: من '{old_display}' إلى '{new_display}'")
                else:
                    changes_list.append(f"{label}: من '{old_value or 'لا شيء'}' إلى '{new_value or 'لا شيء'}'")
        
        form.populate_obj(item)
        if form.contractor_id.data == 0:
            item.contractor_id = None
        
        if changes_list:
            log_item_change(item, 'update', "\n".join(changes_list))

        db.session.commit()
        flash("تم تحديث البند بنجاح!", "success")
        return redirect(url_for("item.edit_item", item_id=item.id))

    if request.method == 'GET' and item.contractor_id:
        form.contractor_id.data = item.contractor_id
        
    contractors = Contractor.query.order_by(Contractor.name).all()

    # --- بداية الإضافة ---
    # هنا نقوم بترتيب تفاصيل التكلفة قبل إرسالها للقالب
    sorted_cost_details = sorted(item.cost_details, key=lambda d: d.id, reverse=True)
    # --- نهاية الإضافة ---

    return render_template("items/edit.html", 
                           item=item, 
                           project=project, 
                           form=form,
                           AuditLog=AuditLog,
                           contractors=contractors,
                           # --- بداية التعديل ---
                           # هنا نمرر القائمة المرتبة بدلاً من الأصلية
                           cost_details=sorted_cost_details,
                           # --- نهاية التعديل ---
                           CostDetail=CostDetail)
# --- END: تحديث دالة edit_item ---

@item_bp.route("/items/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)
    project_id = item.project_id
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
        
    db.session.delete(item)
    db.session.commit()
    flash("تم حذف البند بنجاح.", "success")
    return redirect(url_for("item.get_items_by_project", project_id=project_id))