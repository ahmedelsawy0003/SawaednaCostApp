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
from app.forms import ItemForm # <-- إضافة جديدة

item_bp = Blueprint("item", __name__)

def log_item_change(item, action, changes_details=""):
    """
    Logs changes made to an item.
    For 'update' action, changes_details should be a string describing the changes.
    """
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
    search_number = request.args.get('search_number', '')
    search_description = request.args.get('search_description', '')
    status_filter = request.args.get('status', '')
    contractor_filter = request.args.get('contractor', '')
    query = Item.query.filter_by(project_id=project_id)
    if search_number:
        query = query.filter(Item.item_number.ilike(f"%{search_number}%"))
    if search_description:
        query = query.filter(Item.description.ilike(f"%{search_description}%"))
    if status_filter:
        query = query.filter(Item.status == status_filter)
    if contractor_filter:
        query = query.join(Item.contractor).filter(Contractor.name.ilike(f"%{contractor_filter}%"))
    items = query.order_by(cast(Item.item_number, Integer)).all()
    filters = {
        'search_number': search_number,
        'search_description': search_description,
        'status': status_filter,
        'contractor': contractor_filter
    }
    return render_template("items/index.html", project=project, items=items, filters=filters)


@item_bp.route("/projects/<int:project_id>/items/bulk_update", methods=["POST"])
@login_required
def bulk_update_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    form_data = request.form
    item_ids_str = form_data.getlist('item_ids')
    bulk_status = form_data.get('bulk_status')
    bulk_contractor_id = form_data.get('bulk_contractor_id')
    if not item_ids_str:
        flash("الرجاء تحديد بند واحد على الأقل لتطبيق التعديلات.", "warning")
        return redirect(url_for('item.get_items_by_project', project_id=project_id))
    item_ids = [int(id_str) for id_str in item_ids_str]
    items_to_update = Item.query.filter(Item.id.in_(item_ids)).all()
    update_count = 0
    for item in items_to_update:
        updated = False
        if bulk_status:
            item.status = bulk_status
            updated = True
        if bulk_contractor_id:
            item.contractor_id = int(bulk_contractor_id) if bulk_contractor_id else None
            updated = True
        if updated:
            update_count += 1
    if update_count > 0:
        db.session.commit()
        flash(f"تم تحديث {update_count} بنود بنجاح.", "success")
    else:
        flash("لم يتم إجراء أي تغييرات.", "info")
    return redirect(url_for('item.get_items_by_project', project_id=project_id))

@item_bp.route("/projects/<int:project_id>/items/bulk_delete", methods=["POST"])
@login_required
def bulk_delete_items(project_id):
    if current_user.role != 'admin':
        abort(403)
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    item_ids_str = request.form.getlist('item_ids')
    if not item_ids_str:
        flash("الرجاء تحديد بند واحد على الأقل للحذف.", "warning")
        return redirect(url_for('item.get_items_by_project', project_id=project_id))
    item_ids = [int(id_str) for id_str in item_ids_str]
    items_to_delete = Item.query.filter(Item.id.in_(item_ids), Item.project_id == project_id).all()
    delete_count = len(items_to_delete)
    if delete_count > 0:
        for item in items_to_delete:
            db.session.delete(item)
        db.session.commit()
        flash(f"تم حذف {delete_count} بنود بنجاح.", "success")
    else:
        flash("لم يتم العثور على بنود للحذف.", "info")
    return redirect(url_for('item.get_items_by_project', project_id=project_id))


# --- START: تحديث دالة new_item ---
@item_bp.route("/projects/<int:project_id>/items/new", methods=["GET", "POST"])
@login_required
def new_item(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    
    form = ItemForm()
    form.contractor_id.choices = [(c.id, c.name) for c in Contractor.query.order_by(Contractor.name).all()]
    form.contractor_id.choices.insert(0, (0, '-- تنفيذ ذاتي / بدون مقاول --'))

    if form.validate_on_submit():
        new_item = Item()
        form.populate_obj(new_item) # تعبئة البيانات تلقائياً
        new_item.project_id = project_id
        
        # التأكد من أن القيمة الفارغة للمقاول هي None
        if form.contractor_id.data == 0:
            new_item.contractor_id = None

        db.session.add(new_item)
        db.session.flush() 
        log_item_change(new_item, 'create')
        db.session.commit()
        flash("تم إضافة البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=project_id))

    return render_template("items/new.html", project=project, form=form)
# --- END: تحديث دالة new_item ---


@item_bp.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)
    project = item.project
    
    if request.method == "POST":
        old_values = {
            "رقم البند": item.item_number, "الوصف": item.description, "الوحدة": item.unit,
            "الحالة": item.status, "الملاحظات": item.notes or "",
            "الكمية الفعلية": item.actual_quantity, "التكلفة الفعلية للوحدة": item.actual_unit_cost,
            "المقاول": item.contractor.name if item.contractor else ""
        }
        if current_user.role == 'admin':
            old_values.update({
                "الكمية التعاقدية": item.contract_quantity,
                "التكلفة التعاقدية للوحدة": item.contract_unit_cost
            })

        item.item_number = request.form["item_number"]
        item.description = sanitize_input(request.form["description"])
        item.unit = sanitize_input(request.form["unit"])
        item.status = request.form["status"]
        item.notes = sanitize_input(request.form.get("notes"))
        
        actual_quantity_str = request.form.get("actual_quantity")
        item.actual_quantity = float(actual_quantity_str) if actual_quantity_str else None
        
        actual_unit_cost_str = request.form.get("actual_unit_cost")
        item.actual_unit_cost = float(actual_unit_cost_str) if actual_unit_cost_str else None
        
        contractor_id = request.form.get("contractor_id")
        item.contractor_id = int(contractor_id) if contractor_id else None
        
        if current_user.role == 'admin':
            item.contract_quantity = float(request.form.get("contract_quantity", 0.0))
            item.contract_unit_cost = float(request.form.get("contract_unit_cost", 0.0))

        new_values = {
            "رقم البند": item.item_number, "الوصف": item.description, "الوحدة": item.unit,
            "الحالة": item.status, "الملاحظات": item.notes or "",
            "الكمية الفعلية": item.actual_quantity, "التكلفة الفعلية للوحدة": item.actual_unit_cost,
            "المقاول": item.contractor.name if item.contractor else ""
        }
        if current_user.role == 'admin':
            new_values.update({
                "الكمية التعاقدية": item.contract_quantity,
                "التكلفة التعاقدية للوحدة": item.contract_unit_cost
            })

        changes_list = []
        for key, old_val in old_values.items():
            new_val = new_values.get(key)
            if str(old_val or "") != str(new_val or ""):
                changes_list.append(f"- {key}: من '{old_val or 'لا شيء'}' إلى '{new_val or 'لا شيء'}'")
        
        if changes_list:
            log_item_change(item, 'update', "\n".join(changes_list))

        db.session.commit()
        flash("تم تحديث البند بنجاح!", "success")
        return redirect(url_for("item.edit_item", item_id=item.id))
    
    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template("items/edit.html", 
                           item=item, 
                           project=project, 
                           AuditLog=AuditLog,
                           contractors=contractors,
                           CostDetail=CostDetail)

@item_bp.route("/items/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)
    project_id = item.project_id
    if current_user.role != 'admin':
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash("تم حذف البند بنجاح!", "success")
    return redirect(url_for("item.get_items_by_project", project_id=project_id))