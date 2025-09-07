from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models.item import Item
from app.models.cost_detail import CostDetail
from app.models.contractor import Contractor
from app.models.audit_log import AuditLog
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input

cost_detail_bp = Blueprint("cost_detail", __name__, url_prefix='/cost_details')

def log_cost_detail_change(item_id, action, details):
    """Logs changes related to a cost detail to the parent item's audit log."""
    if not details:
        return
        
    log_entry = AuditLog(
        item_id=item_id,
        user_id=current_user.id,
        action='update', 
        details=details
    )
    db.session.add(log_entry)

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
        # --- START: جلب قيمة الضريبة ---
        vat_percent_str = request.form.get("vat_percent")
        # --- END: جلب قيمة الضريبة ---
        contractor_id_str = request.form.get("contractor_id")
        
        purchase_order = sanitize_input(request.form.get("purchase_order_number"))
        disbursement_order = sanitize_input(request.form.get("disbursement_order_number"))

        if not all([description, quantity_str, unit_cost_str]):
            flash("الوصف، الكمية، وتكلفة الوحدة هي حقول مطلوبة.", "danger")
            return redirect(url_for("item.edit_item", item_id=item_id))

        quantity = float(quantity_str)
        unit_cost = float(unit_cost_str)
        # --- START: معالجة قيمة الضريبة ---
        vat_percent = float(vat_percent_str) if vat_percent_str else 0.0
        # --- END: معالجة قيمة الضريبة ---
        contractor_id = int(contractor_id_str) if contractor_id_str else None

        new_detail = CostDetail(
            item_id=item.id,
            description=description,
            unit=unit,
            quantity=quantity,
            unit_cost=unit_cost,
            # --- START: حفظ قيمة الضريبة ---
            vat_percent=vat_percent,
            # --- END: حفظ قيمة الضريبة ---
            contractor_id=contractor_id,
            purchase_order_number=purchase_order,
            disbursement_order_number=disbursement_order
        )
        db.session.add(new_detail)
        
        log_details = f"تمت إضافة تفصيل تكلفة جديد: '{description}' (الكمية: {quantity}, التكلفة: {unit_cost}, الضريبة: {vat_percent}%)"
        log_cost_detail_change(item_id, 'create', log_details)

        db.session.commit()
        flash("تمت إضافة تفصيل التكلفة بنجاح!", "success")

    except (ValueError, TypeError):
        flash("الرجاء إدخال قيم رقمية صالحة للكمية والتكلفة والضريبة.", "danger")
    
    return redirect(url_for("item.edit_item", item_id=item_id))

@cost_detail_bp.route("/<int:detail_id>/edit", methods=["GET", "POST"])
@login_required
def edit_cost_detail(detail_id):
    """Edits an existing cost detail."""
    detail = CostDetail.query.get_or_404(detail_id)
    check_project_permission(detail.item.project)

    if request.method == "POST":
        try:
            old_desc = detail.description
            old_qty = detail.quantity
            old_cost = detail.unit_cost
            # --- START: جلب القيمة القديمة للضريبة ---
            old_vat = detail.vat_percent
            # --- END: جلب القيمة القديمة للضريبة ---

            detail.description = sanitize_input(request.form.get("description"))
            detail.unit = sanitize_input(request.form.get("unit"))
            detail.quantity = float(request.form.get("quantity"))
            detail.unit_cost = float(request.form.get("unit_cost"))
            # --- START: تحديث قيمة الضريبة ---
            detail.vat_percent = float(request.form.get("vat_percent") or 0.0)
            # --- END: تحديث قيمة الضريبة ---
            contractor_id_str = request.form.get("contractor_id")
            detail.contractor_id = int(contractor_id_str) if contractor_id_str else None
            
            detail.purchase_order_number = sanitize_input(request.form.get("purchase_order_number"))
            detail.disbursement_order_number = sanitize_input(request.form.get("disbursement_order_number"))
            
            changes = []
            if old_desc != detail.description:
                changes.append(f"وصف التفصيل تغير من '{old_desc}' إلى '{detail.description}'")
            if old_qty != detail.quantity:
                changes.append(f"كمية التفصيل '{detail.description}' تغيرت من {old_qty} إلى {detail.quantity}")
            if old_cost != detail.unit_cost:
                changes.append(f"تكلفة التفصيل '{detail.description}' تغيرت من {old_cost} إلى {detail.unit_cost}")
            # --- START: تسجيل تغيير الضريبة ---
            if old_vat != detail.vat_percent:
                changes.append(f"ضريبة التفصيل '{detail.description}' تغيرت من {old_vat}% إلى {detail.vat_percent}%")
            # --- END: تسجيل تغيير الضريبة ---
            
            if changes:
                log_cost_detail_change(detail.item_id, 'update', "\n".join(changes))

            db.session.commit()
            flash("تم تحديث تفصيل التكلفة بنجاح.", "success")
            return redirect(url_for("item.edit_item", item_id=detail.item_id))

        except (ValueError, TypeError):
            flash("الرجاء إدخال قيم رقمية صالحة للكمية والتكلفة والضريبة.", "danger")
    
    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template("cost_details/edit.html", detail=detail, contractors=contractors)


@cost_detail_bp.route("/<int:detail_id>/delete", methods=["POST"])
@login_required
def delete_cost_detail(detail_id):
    detail = CostDetail.query.get_or_404(detail_id)
    item_id = detail.item_id
    check_project_permission(detail.item.project)

    log_details = f"تم حذف تفصيل التكلفة: '{detail.description}'"
    log_cost_detail_change(item_id, 'delete', log_details)

    db.session.delete(detail)
    db.session.commit()
    flash("تم حذف تفصيل التكلفة بنجاح.", "success")
    
    return redirect(url_for("item.edit_item", item_id=item_id))