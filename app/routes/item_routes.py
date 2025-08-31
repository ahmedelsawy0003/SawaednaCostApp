from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import cast, Integer
from app.models.item import Item
from app.models.project import Project
from app.models.audit_log import AuditLog
from app.models.contractor import Contractor
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input

item_bp = Blueprint("item", __name__)

# ... (log_item_change function remains the same) ...
def log_item_change(item, action):
    details = []
    if action == 'create':
        details.append("تم إنشاء البند.")
    elif action == 'update':
        pass
    
    if not details:
        return

    log_entry = AuditLog(
        item_id=item.id,
        user_id=current_user.id,
        action=action,
        details="\n".join(details)
    )
    db.session.add(log_entry)


@item_bp.route("/projects/<int:project_id>/items")
@login_required
def get_items_by_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)

    # Get filter values from URL arguments
    search_number = request.args.get('search_number', '')
    search_description = request.args.get('search_description', '')
    status_filter = request.args.get('status', '')
    
    contractor_filter = request.args.get('contractor', '')

    query = Item.query.filter_by(project_id=project_id)

    # Apply filters based on user input
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

# --- START: دالة الحذف الجماعي الجديدة ---
@item_bp.route("/projects/<int:project_id>/items/bulk_delete", methods=["POST"])
@login_required
def bulk_delete_items(project_id):
    # التأكد من أن المستخدم له صلاحية admin
    if current_user.role != 'admin':
        abort(403)

    project = Project.query.get_or_404(project_id)
    check_project_permission(project)

    item_ids_str = request.form.getlist('item_ids')
    if not item_ids_str:
        flash("الرجاء تحديد بند واحد على الأقل للحذف.", "warning")
        return redirect(url_for('item.get_items_by_project', project_id=project_id))

    item_ids = [int(id_str) for id_str in item_ids_str]
    
    # جلب البنود المراد حذفها والتأكد من أنها تابعة للمشروع الصحيح
    items_to_delete = Item.query.filter(Item.id.in_(item_ids), Item.project_id == project_id).all()
    
    delete_count = len(items_to_delete)
    
    if delete_count > 0:
        for item in items_to_delete:
            # سيقوم cascade بحذف السجلات المرتبطة تلقائياً
            db.session.delete(item)
        db.session.commit()
        flash(f"تم حذف {delete_count} بنود بنجاح.", "success")
    else:
        flash("لم يتم العثور على بنود للحذف.", "info")

    return redirect(url_for('item.get_items_by_project', project_id=project_id))
# --- END: دالة الحذف الجماعي الجديدة ---


@item_bp.route("/projects/<int:project_id>/items/new", methods=["GET", "POST"])
@login_required
def new_item(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    if request.method == "POST":
        description = sanitize_input(request.form["description"])
        unit = sanitize_input(request.form["unit"])
        notes = sanitize_input(request.form.get("notes"))
        contract_quantity = float(request.form.get("contract_quantity", 0.0))
        contract_unit_cost = float(request.form.get("contract_unit_cost", 0.0))
        item_number = request.form["item_number"]
        actual_quantity = float(request.form.get("actual_quantity") or 0.0)
        actual_unit_cost = float(request.form.get("actual_unit_cost") or 0.0)
        status = request.form["status"]
        
        contractor_id = request.form.get("contractor_id")

        new_item = Item(project_id=project_id, item_number=item_number, description=description,
                        unit=unit, contract_quantity=contract_quantity, contract_unit_cost=contract_unit_cost,
                        actual_quantity=actual_quantity, actual_unit_cost=actual_unit_cost, status=status,
                        notes=notes,
                        contractor_id=int(contractor_id) if contractor_id else None)
        db.session.add(new_item)
        db.session.flush()
        db.session.commit()
        flash("تم إضافة البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=project_id))

    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template("items/new.html", project=project, contractors=contractors)


@item_bp.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)
    project = item.project
    if request.method == "POST":
        
        item.description = sanitize_input(request.form["description"])
        item.unit = sanitize_input(request.form["unit"])
        item.notes = sanitize_input(request.form.get("notes"))
        if current_user.role == 'admin':
            item.contract_unit_cost = float(request.form.get("contract_unit_cost", 0.0))
        item.item_number = request.form["item_number"]
        item.contract_quantity = float(request.form.get("contract_quantity", 0.0))
        item.actual_quantity = float(request.form.get("actual_quantity") or 0.0)
        item.actual_unit_cost = float(request.form.get("actual_unit_cost") or 0.0)
        item.status = request.form["status"]
        
        contractor_id = request.form.get("contractor_id")
        item.contractor_id = int(contractor_id) if contractor_id else None
        
        db.session.commit()
        flash("تم تحديث البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=item.project_id))
    
    contractors = Contractor.query.order_by(Contractor.name).all()
    
    return render_template("items/edit.html", 
                           item=item, 
                           project=project, 
                           AuditLog=AuditLog,
                           contractors=contractors)

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


@item_bp.route("/items/<int:item_id>/details")
@login_required
def get_item_details(item_id):
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)
    # --- START: التعديل الرئيسي ---
    # تم حذف paid_amount و remaining_amount من الاستجابة
    return jsonify({
        "item_number": item.item_number,
        "description": item.description,
        "unit": item.unit,
        "contract_quantity": item.contract_quantity,
        "contract_unit_cost": item.contract_unit_cost,
        "contract_total_cost": item.contract_total_cost,
        "actual_quantity": item.actual_quantity,
        "actual_unit_cost": item.actual_unit_cost,
        "actual_total_cost": item.actual_total_cost,
        "cost_variance": item.cost_variance,
        "quantity_variance": item.quantity_variance,
        "status": item.status,
        "execution_method": item.execution_method,
        "contractor": item.contractor.name if item.contractor else None,
        "notes": item.notes
    })
    # --- END: التعديل الرئيسي ---