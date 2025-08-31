from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models.item import Item
from app.models.cost_detail import CostDetail
from app.models.contractor import Contractor
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input

cost_detail_bp = Blueprint("cost_detail", __name__, url_prefix='/cost_details')

@cost_detail_bp.route("/item/<int:item_id>/add", methods=["POST"])
@login_required
def add_cost_detail(item_id):
    """Adds a new cost detail to a specific item."""
    item = Item.query.get_or_404(item_id)
    check_project_permission(item.project)

    try:
        description = sanitize_input(request.form.get("description"))
        unit = sanitize_input(request.form.get("unit"))
        quantity_str = request.form.get("quantity")
        unit_cost_str = request.form.get("unit_cost")
        contractor_id_str = request.form.get("contractor_id")

        if not all([description, quantity_str, unit_cost_str]):
            flash("الوصف، الكمية، وتكلفة الوحدة هي حقول مطلوبة.", "danger")
            return redirect(url_for("item.edit_item", item_id=item_id))

        quantity = float(quantity_str)
        unit_cost = float(unit_cost_str)
        contractor_id = int(contractor_id_str) if contractor_id_str else None

        new_detail = CostDetail(
            item_id=item.id,
            description=description,
            unit=unit,
            quantity=quantity,
            unit_cost=unit_cost,
            contractor_id=contractor_id
        )
        db.session.add(new_detail)
        db.session.commit()
        flash("تمت إضافة تفصيل التكلفة بنجاح!", "success")

    except (ValueError, TypeError):
        flash("الرجاء إدخال قيم رقمية صالحة للكمية والتكلفة.", "danger")
    
    return redirect(url_for("item.edit_item", item_id=item_id))

@cost_detail_bp.route("/<int:detail_id>/edit", methods=["GET", "POST"])
@login_required
def edit_cost_detail(detail_id):
    """Edits an existing cost detail."""
    detail = CostDetail.query.get_or_404(detail_id)
    check_project_permission(detail.item.project)

    if request.method == "POST":
        try:
            detail.description = sanitize_input(request.form.get("description"))
            detail.unit = sanitize_input(request.form.get("unit"))
            detail.quantity = float(request.form.get("quantity"))
            detail.unit_cost = float(request.form.get("unit_cost"))
            contractor_id_str = request.form.get("contractor_id")
            detail.contractor_id = int(contractor_id_str) if contractor_id_str else None
            
            db.session.commit()
            flash("تم تحديث تفصيل التكلفة بنجاح.", "success")
            return redirect(url_for("item.edit_item", item_id=detail.item_id))

        except (ValueError, TypeError):
            flash("الرجاء إدخال قيم رقمية صالحة للكمية والتكلفة.", "danger")
    
    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template("cost_details/edit.html", detail=detail, contractors=contractors)


@cost_detail_bp.route("/<int:detail_id>/delete", methods=["POST"])
@login_required
def delete_cost_detail(detail_id):
    """Deletes a cost detail."""
    detail = CostDetail.query.get_or_404(detail_id)
    item_id = detail.item_id
    check_project_permission(detail.item.project)

    db.session.delete(detail)
    db.session.commit()
    flash("تم حذف تفصيل التكلفة بنجاح.", "success")
    
    return redirect(url_for("item.edit_item", item_id=item_id))