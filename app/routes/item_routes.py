from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import cast, Integer # <<< Add this import
from app.models.item import Item
from app.models.project import Project
from app.models.cost_detail import CostDetail
from app.models.audit_log import AuditLog
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input

item_bp = Blueprint("item", __name__)

# ... (The log_item_change function remains the same) ...
def log_item_change(item, action):
    details = []
    if action == 'create':
        details.append("تم إنشاء البند.")
    elif action == 'update':
        changes = db.session.dirty.copy()
        for attr in changes:
            history = getattr(attr.history, 'deleted', [])
            if history:
                old_value = history[0]
                new_value = getattr(attr, attr.key)
                if old_value != new_value:
                     details.append(f"تم تغيير '{attr.key}' من '{old_value}' إلى '{new_value}'.")
    
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

    search_term = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    contractor_filter = request.args.get('contractor', '')

    query = Item.query.filter_by(project_id=project_id)

    if search_term:
        search_like = f"%{search_term}%"
        query = query.filter(db.or_(
            Item.item_number.ilike(search_like),
            Item.description.ilike(search_like)
        ))
    
    if status_filter:
        query = query.filter(Item.status == status_filter)

    if contractor_filter:
        contractor_like = f"%{contractor_filter}%"
        query = query.filter(Item.contractor.ilike(contractor_like))

    # START: Modified sorting to be numerical
    items = query.order_by(cast(Item.item_number, Integer)).all()
    # END: Modified sorting

    filters = {
        'search': search_term,
        'status': status_filter,
        'contractor': contractor_filter
    }
    return render_template("items/index.html", project=project, items=items, filters=filters)

# ... (The rest of the file remains exactly the same) ...
@item_bp.route("/projects/<int:project_id>/items/new", methods=["GET", "POST"])
@login_required
def new_item(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    if request.method == "POST":
        description = sanitize_input(request.form["description"])
        unit = sanitize_input(request.form["unit"])
        execution_method = sanitize_input(request.form.get("execution_method"))
        contractor = sanitize_input(request.form.get("contractor"))
        notes = sanitize_input(request.form.get("notes"))
        contract_quantity = float(request.form.get("contract_quantity", 0.0))
        contract_unit_cost = float(request.form.get("contract_unit_cost", 0.0))
        item_number = request.form["item_number"]
        actual_quantity = float(request.form.get("actual_quantity") or 0.0)
        actual_unit_cost = float(request.form.get("actual_unit_cost") or 0.0)
        status = request.form["status"]

        new_item = Item(project_id=project_id, item_number=item_number, description=description,
                        unit=unit, contract_quantity=contract_quantity, contract_unit_cost=contract_unit_cost,
                        actual_quantity=actual_quantity, actual_unit_cost=actual_unit_cost, status=status,
                        execution_method=execution_method, contractor=contractor, notes=notes)
        db.session.add(new_item)
        db.session.flush()
        log_item_change(new_item, 'create')
        db.session.commit()
        flash("تم إضافة البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=project_id))
    return render_template("items/new.html", project=project)

@item_bp.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)
    project = item.project
    if request.method == "POST":
        log_item_change(item, 'update')
        
        item.description = sanitize_input(request.form["description"])
        item.unit = sanitize_input(request.form["unit"])
        item.execution_method = sanitize_input(request.form.get("execution_method"))
        item.contractor = sanitize_input(request.form.get("contractor"))
        item.notes = sanitize_input(request.form.get("notes"))
        if current_user.role == 'admin':
            item.contract_unit_cost = float(request.form.get("contract_unit_cost", 0.0))
        item.item_number = request.form["item_number"]
        item.contract_quantity = float(request.form.get("contract_quantity", 0.0))
        item.actual_quantity = float(request.form.get("actual_quantity") or 0.0)
        item.actual_unit_cost = float(request.form.get("actual_unit_cost") or 0.0)
        item.status = request.form["status"]
        
        db.session.commit()
        flash("تم تحديث البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=item.project_id))
    
    cost_details = CostDetail.query.filter_by(item_id=item.id).order_by(CostDetail.id.desc()).all()
    
    return render_template("items/edit.html", 
                           item=item, 
                           project=project, 
                           cost_details=cost_details, 
                           AuditLog=AuditLog)

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
        "contractor": item.contractor,
        "paid_amount": item.paid_amount,
        "remaining_amount": item.remaining_amount,
        "notes": item.notes
    })