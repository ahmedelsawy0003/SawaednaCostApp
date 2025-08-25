from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from app.models.item import Item
from app.models.project import Project
from app.models.cost_detail import CostDetail
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input

item_bp = Blueprint("item", __name__)

@item_bp.route("/projects/<int:project_id>/items")
@login_required
def get_items_by_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    items = Item.query.filter_by(project_id=project_id).all()
    return render_template("items/index.html", project=project, items=items)

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
        paid_amount = float(request.form.get("paid_amount") or 0.0)

        new_item = Item(project_id=project_id, item_number=item_number, description=description,
                        unit=unit, contract_quantity=contract_quantity, contract_unit_cost=contract_unit_cost,
                        actual_quantity=actual_quantity, actual_unit_cost=actual_unit_cost, status=status,
                        execution_method=execution_method, contractor=contractor, paid_amount=paid_amount, notes=notes)
        db.session.add(new_item)
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
        item.paid_amount = float(request.form.get("paid_amount") or 0.0)

        db.session.commit()
        flash("تم تحديث البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=item.project_id))
    
    # START: Corrected query
    # Sort by ID to show the newest details first
    cost_details = CostDetail.query.filter_by(item_id=item.id).order_by(CostDetail.id.desc()).all()
    return render_template("items/edit.html", item=item, project=project, cost_details=cost_details)
    # END: Corrected query

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