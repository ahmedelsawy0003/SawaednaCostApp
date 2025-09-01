from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from sqlalchemy import func
from app.models.project import Project
from app.models.contractor import Contractor
from app.models.item import Item
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
# --- START: استيراد موديل تفاصيل التكلفة ---
from app.models.cost_detail import CostDetail
# --- END: استيراد موديل تفاصيل التكلفة ---
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input
import datetime

invoice_bp = Blueprint("invoice", __name__, url_prefix='/invoices')

# ... (get_invoices_by_project, new_invoice, delete_invoice remain the same) ...
@invoice_bp.route("/project/<int:project_id>")
@login_required
def get_invoices_by_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    invoices = project.invoices.order_by(Invoice.invoice_date.desc()).all()
    return render_template("invoices/index.html", project=project, invoices=invoices)

@invoice_bp.route("/<int:invoice_id>")
@login_required
def show_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)

    # --- START: جلب نوعين من البنود المتاحة ---
    # 1. جلب البنود الرئيسية التي لم تضف للمستخلص بعد
    added_main_items_subquery = db.session.query(InvoiceItem.item_id).filter(
        InvoiceItem.invoice_id == invoice.id,
        InvoiceItem.cost_detail_id.is_(None) # Ensure it's a main item link
    )
    available_items = Item.query.filter(
        Item.project_id == invoice.project_id,
        Item.contractor_id == invoice.contractor_id,
        ~Item.id.in_(added_main_items_subquery)
    ).order_by(Item.item_number).all()

    # 2. جلب تفاصيل التكلفة (أوامر العمل) المسندة للمقاول والتي لم تضف للمستخلص بعد
    added_cost_details_subquery = db.session.query(InvoiceItem.cost_detail_id).filter(
        InvoiceItem.invoice_id == invoice.id,
        InvoiceItem.cost_detail_id.isnot(None) # Ensure it's a cost detail link
    )
    available_cost_details = CostDetail.query.filter(
        CostDetail.contractor_id == invoice.contractor_id,
        CostDetail.item.has(project_id=invoice.project_id),
        ~CostDetail.id.in_(added_cost_details_subquery)
    ).order_by(CostDetail.id).all()
    # --- END: جلب نوعين من البنود المتاحة ---

    return render_template(
        "invoices/show.html", 
        invoice=invoice, 
        available_items=available_items, 
        available_cost_details=available_cost_details
    )

# --- START: تعديل دالة إضافة البنود لتصبح أذكى ---
@invoice_bp.route("/<int:invoice_id>/add_item", methods=["POST"])
@login_required
def add_item_to_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)
    
    selected_id_str = request.form.get("selected_item_id")
    quantity_str = request.form.get("quantity")

    if not selected_id_str or not quantity_str:
        flash("الرجاء اختيار بند وإدخال الكمية.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    try:
        new_quantity = float(quantity_str)
        if new_quantity <= 0:
            flash("يجب أن تكون الكمية أكبر من صفر.", "danger")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
    except ValueError:
        flash("الكمية المدخلة غير صالحة.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    # تحديد نوع البند المختار (رئيسي أم تفصيل تكلفة)
    if selected_id_str.startswith('item_'):
        item_id = int(selected_id_str.split('_')[1])
        item = Item.query.get_or_404(item_id)
        
        # التحقق من الكمية للبند الرئيسي
        max_quantity = item.actual_quantity
        if max_quantity is None or max_quantity <= 0:
            flash(f"لا يمكن فوترة البند '{item.item_number}' لعدم وجود 'كمية فعلية' مسجلة له.", "danger")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

        previously_invoiced_qty = db.session.query(func.sum(InvoiceItem.quantity)).filter(InvoiceItem.item_id == item.id, InvoiceItem.cost_detail_id.is_(None)).scalar() or 0.0

        if (previously_invoiced_qty + new_quantity) > max_quantity:
            remaining_qty = max_quantity - previously_invoiced_qty
            flash(f"كمية البند الرئيسي تتجاوز الحد المسموح. المتبقي: {remaining_qty:.2f}", "danger")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
        
        new_invoice_item = InvoiceItem(quantity=new_quantity, item=item)
        flash_message = f"تمت إضافة البند الرئيسي '{item.item_number}' للمستخلص."

    elif selected_id_str.startswith('detail_'):
        detail_id = int(selected_id_str.split('_')[1])
        cost_detail = CostDetail.query.get_or_404(detail_id)

        # التحقق من الكمية لتفصيل التكلفة
        max_quantity = cost_detail.quantity
        previously_invoiced_qty = db.session.query(func.sum(InvoiceItem.quantity)).filter(InvoiceItem.cost_detail_id == detail_id).scalar() or 0.0

        if (previously_invoiced_qty + new_quantity) > max_quantity:
            remaining_qty = max_quantity - previously_invoiced_qty
            flash(f"كمية تفصيل التكلفة تتجاوز الحد المسموح. المتبقي: {remaining_qty:.2f}", "danger")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

        new_invoice_item = InvoiceItem(quantity=new_quantity, cost_detail=cost_detail)
        flash_message = f"تمت إضافة تفصيل التكلفة '{cost_detail.description}' للمستخلص."
    
    else:
        flash("اختيار غير صالح.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    new_invoice_item.invoice_id = invoice.id
    db.session.add(new_invoice_item)
    db.session.commit()
    flash(flash_message, "success")
    return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
# --- END: تعديل دالة إضافة البنود ---


@invoice_bp.route("/<int:invoice_id>/add_payment", methods=["POST"])
@login_required
def add_payment_to_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)
    amount_str = request.form.get("amount")
    payment_date_str = request.form.get("payment_date")
    description = sanitize_input(request.form.get("description"))
    invoice_item_id = request.form.get("invoice_item_id")
    if not amount_str or not payment_date_str:
        flash("المبلغ وتاريخ الدفعة حقول مطلوبة.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
    try:
        amount = float(amount_str)
        payment_date = datetime.datetime.strptime(payment_date_str, "%Y-%m-%d").date()
        if amount <= 0:
            flash("يجب أن يكون مبلغ الدفعة أكبر من صفر.", "danger")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
    except (ValueError, TypeError):
        flash("البيانات المدخلة للمبلغ أو التاريخ غير صالحة.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
    total_invoice_amount = invoice.total_amount or 0.0
    paid_amount = invoice.paid_amount or 0.0
    if (paid_amount + amount) > total_invoice_amount:
        remaining_to_pay = total_invoice_amount - paid_amount
        flash(f"لا يمكن إضافة هذه الدفعة. المبلغ الإجمالي للمستخلص هو {total_invoice_amount:,.2f} ريال. تم دفع {paid_amount:,.2f} ريال بالفعل. أقصى مبلغ يمكن دفعه الآن هو {remaining_to_pay:,.2f} ريال.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
    new_payment = Payment(
        invoice_id=invoice.id,
        amount=amount,
        payment_date=payment_date,
        description=description,
        invoice_item_id=int(invoice_item_id) if invoice_item_id else None
    )
    db.session.add(new_payment)
    db.session.commit()
    flash("تم تسجيل الدفعة بنجاح.", "success")
    return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))


# ... (The rest of the file remains the same) ...
@invoice_bp.route("/payments/<int:payment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    invoice = payment.invoice
    check_project_permission(invoice.project)
    if request.method == "POST":
        amount_str = request.form.get("amount")
        payment_date_str = request.form.get("payment_date")
        description = sanitize_input(request.form.get("description"))
        if not amount_str or not payment_date_str:
            flash("المبلغ وتاريخ الدفعة حقول مطلوبة.", "danger")
            return redirect(url_for('invoice.edit_payment', payment_id=payment.id))
        try:
            payment.amount = float(amount_str)
            payment.payment_date = datetime.datetime.strptime(payment_date_str, "%Y-%m-%d").date()
            payment.description = description
            db.session.commit()
            flash("تم تحديث الدفعة بنجاح.", "success")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice.id))
        except (ValueError, TypeError):
            flash("البيانات المدخلة للمبلغ أو التاريخ غير صالحة.", "danger")
    return render_template("invoices/edit_payment.html", payment=payment)