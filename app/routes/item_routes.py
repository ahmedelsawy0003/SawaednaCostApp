from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import cast, Integer, func
from app.models.item import Item
from app.models.project import Project
from app.models.audit_log import AuditLog
from app.models.contractor import Contractor
from app.models.cost_detail import CostDetail 
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input
from app.forms import ItemForm
from sqlalchemy.orm import undefer # <<< إضافة: استيراد دالة التحميل الصريح

item_bp = Blueprint("item", __name__)

def log_item_change(item, action, changes_details=""):
    details = ""
    if action == 'create':
        details = f"تم إنشاء البند '{item.item_number}'."
    elif action == 'update':
        # UX IMPROVEMENT: Arabic message for log details
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

    # قراءة جميع الفلاتر من الرابط
    search_number = request.args.get('search_number', '')
    search_description = request.args.get('search_description', '')
    status = request.args.get('status', '')
    contractor_search = request.args.get('contractor', '')

    query = Item.query.filter_by(project_id=project_id)

    # تطبيق الفلاتر على الاستعلام
    if search_number:
        query = query.filter(Item.item_number.ilike(f"%{search_number}%"))
    if search_description:
        query = query.filter(Item.description.ilike(f"%{search_description}%"))
    if status:
        query = query.filter(Item.status == status)
    if contractor_search:
        # الانضمام إلى جدول المقاولين للبحث بالاسم
        query = query.join(Item.contractor).filter(Contractor.name.ilike(f"%{contractor_search}%"))

    # إنشاء قاموس الفلاتر لإرساله للقالب
    filters = {
        'search_number': search_number,
        'search_description': search_description,
        'status': status,
        'contractor': contractor_search
    }

    # Use substring to extract leading numbers for a safe numerical sort
    numeric_part = func.substring(Item.item_number, '^[0-9]+')
    
    # <<< New performance optimization line: explicitly load paid_amount and actual_details_cost
    items = query.options(
        undefer(Item.paid_amount), 
        undefer(Item.actual_details_cost)
    ).order_by(cast(numeric_part, Integer), Item.item_number).all()
    
    # إرسال قاموس "filters" بدلاً من "search_query"
    return render_template("items/index.html", items=items, project=project, filters=filters)

@item_bp.route("/projects/<int:project_id>/items/bulk_add", methods=['GET', 'POST'])
@login_required
def bulk_add_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project, require_admin=True)

    if request.method == 'POST':
        items_data = request.form.get('items_data')
        if not items_data:
            # UX IMPROVEMENT: Clearer warning
            flash('لا توجد بيانات لإضافتها. يرجى لصق البيانات في الحقل المخصص.', 'warning')
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
                    # UX IMPROVEMENT: Clearer error message
                    flash(f'خطأ في بيانات أحد الأسطر: {line}. الرجاء التأكد من أن الكمية والسعر أرقام صالحة.', 'danger')
                    continue
        
        if added_count > 0:
            db.session.commit()
            flash(f'تمت إضافة {added_count} بندًا بنجاح.', 'success')
        
        return redirect(url_for('item.get_items_by_project', project_id=project_id))

@item_bp.route('/projects/<int:project_id>/items/bulk_update', methods=['GET', 'POST'])
@login_required
def bulk_update_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project, require_admin=True)

    if request.method == 'POST':
        items_data = request.form.get('items_data_update')
        if not items_data:
            # UX IMPROVEMENT: Clearer warning
            flash('لا توجد بيانات لتحديثها. يرجى لصق البيانات في الحقل المخصص.', 'warning')
            return redirect(url_for('item.bulk_update_items', project_id=project_id))

        lines = items_data.strip().split('\n')
        updated_count = 0
        for line in lines:
            parts = line.strip().split('\t')
            # Check for at least item_number, actual_quantity, and actual_unit_cost (3 parts)
            if len(parts) >= 3:
                item_number = sanitize_input(parts[0])
                item = Item.query.filter_by(project_id=project_id, item_number=item_number).first()
                if item:
                    try:
                        changes = []
                        
                        # --- START: Streamlined Update Logic ---
                        fields_to_update = [
                            ('actual_quantity', parts[1].strip(), 'الكمية المتاحة للفوترة'),
                            ('actual_unit_cost', parts[2].strip(), 'تكلفة الوحدة للمستخلص'),
                        ]

                        for field_name, new_value_str, display_name in fields_to_update:
                            if new_value_str:
                                # Get the original value and safely parse the new value
                                original_value = getattr(item, field_name)
                                new_value = float(new_value_str)

                                # Compare (using tolerance for floats and checking for None)
                                if (original_value is None or abs(new_value - original_value) > 0.001):
                                    setattr(item, field_name, new_value)
                                    original_display = f"'{original_value}'" if original_value is not None else "'لا شيء'"
                                    changes.append(f"{display_name}: من {original_display} إلى '{new_value}'")

                        # --- END: Streamlined Update Logic ---
                        
                        if changes:
                            log_item_change(item, 'update', "\n".join(changes))
                            updated_count += 1

                    except (ValueError, IndexError):
                        # UX IMPROVEMENT: Clearer error message
                        flash(f'بيانات غير صالحة للكمية الفعلية أو تكلفة الوحدة الفعلية للبند {item_number}. يجب أن تكون أرقامًا.', 'danger')
                        continue
        
        if updated_count > 0:
            db.session.commit()
            # UX Improvement: Confirm that changes were logged
            flash(f'تم تحديث {updated_count} بندًا بنجاح. تم تسجيل التغييرات في سجل التغييرات.', 'success')

        return redirect(url_for('item.get_items_by_project', project_id=project_id))
    
    items = Item.query.filter_by(project_id=project_id).order_by(Item.item_number).all()
    return render_template('items/bulk_update.html', project=project, items=items)

@item_bp.route('/projects/<int:project_id>/items/bulk_delete', methods=['POST'])
@login_required
def bulk_delete_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project, require_admin=True)

    item_ids = [int(id) for id in request.form.getlist('item_ids')]
    if not item_ids:
        # UX IMPROVEMENT: Clearer warning
        flash('الرجاء تحديد بند واحد على الأقل لحذفه.', 'warning')
        return redirect(url_for('item.get_items_by_project', project_id=project_id))

    # Query all items to be deleted in one go for efficiency
    items_to_delete = Item.query.filter(Item.id.in_(item_ids)).all()
    
    deleted_count = 0
    for item in items_to_delete:
        # Ensure the item belongs to the correct project for security
        if item.project_id == int(project_id):
            db.session.delete(item)
            deleted_count += 1
    
    if deleted_count > 0:
        db.session.commit()
        # UX IMPROVEMENT: Clearer success message
        flash(f'تم حذف {deleted_count} بندًا وكل ما يتعلق بها بنجاح.', 'success')

    return redirect(url_for('item.get_items_by_project', project_id=project_id))


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
            # UX IMPROVEMENT: Clearer field labels for log
            'item_number': 'رقم البند', 'description': 'الوصف', 'unit': 'الوحدة',
            'contract_quantity': 'الكمية التعاقدية', 'contract_unit_cost': 'تكلفة الوحدة التعاقدية',
            'actual_quantity': 'الكمية المتاحة للفوترة', 'actual_unit_cost': 'تكلفة الوحدة للمستخلص',
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
        # UX IMPROVEMENT: Clearer message
        flash("تم تحديث البند بنجاح! تم تسجيل التغييرات في سجل التغييرات.", "success")
        return redirect(url_for("item.edit_item", item_id=item.id))

    if request.method == 'GET' and item.contractor_id:
        form.contractor_id.data = item.contractor_id
        
    contractors = Contractor.query.order_by(Contractor.name).all()

    # هنا نقوم بترتيب تفاصيل التكلفة قبل إرسالها للقالب
    sorted_cost_details = sorted(item.cost_details, key=lambda d: d.id, reverse=True)

    return render_template("items/edit.html", 
                           item=item, 
                           project=project, 
                           form=form,
                           AuditLog=AuditLog,
                           contractors=contractors,
                           cost_details=sorted_cost_details,
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
    # UX IMPROVEMENT: Clearer message
    flash("تم حذف البند وكل ما يتعلق به بنجاح.", "success")
    return redirect(url_for("item.get_items_by_project", project_id=project_id))
    
@item_bp.route("/projects/<int:project_id>/items/bulk_duplicate", methods=['POST'])
@login_required
def bulk_duplicate_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project, require_admin=True)

    item_ids = request.form.getlist('item_ids')
    if not item_ids:
        flash('الرجاء تحديد بند واحد على الأقل لتكراره.', 'warning')
        return redirect(url_for('item.get_items_by_project', project_id=project_id))

    duplicated_count = 0
    for item_id in item_ids:
        original_item = Item.query.get(item_id)
        if original_item:
            
            # Step 1: Prepare the new item number BEFORE creating the object
            base_number = f"{original_item.item_number}-نسخة"
            existing_copies_count = Item.query.filter(
                Item.project_id == int(project_id), 
                Item.item_number.like(f"{base_number}%")
            ).count()
            new_item_number = f"{base_number}-{existing_copies_count + 1}"

            # Step 2: Create the new item object with the prepared number
            new_item = Item(
                project_id=original_item.project_id,
                item_number=new_item_number,
                description=original_item.description,
                unit=original_item.unit,
                contract_quantity=original_item.contract_quantity,
                contract_unit_cost=original_item.contract_unit_cost,
                actual_quantity=original_item.actual_quantity,
                actual_unit_cost=original_item.actual_unit_cost,
                status=original_item.status,
                notes=original_item.notes,
                purchase_order_number=original_item.purchase_order_number,
                disbursement_order_number=original_item.disbursement_order_number,
                contractor_id=original_item.contractor_id
            )
            db.session.add(new_item)
            duplicated_count += 1
    
    if duplicated_count > 0:
        db.session.commit()
        # UX IMPROVEMENT: Clearer success message
        flash(f'تم تكرار {duplicated_count} بندًا بنجاح.', 'success')

    return redirect(url_for('item.get_items_by_project', project_id=project_id))