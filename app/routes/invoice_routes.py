from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from sqlalchemy import func
from app.models.project import Project
from app.models.contractor import Contractor
from app.models.item import Item
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
from app.models.cost_detail import CostDetail
# --- START: NEW MODEL IMPORT ---
from app.models.payment_distribution import PaymentDistribution
# --- END: NEW MODEL IMPORT ---
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input
import datetime

invoice_bp = Blueprint("invoice", __name__, url_prefix='/invoices')

# ... other functions (get_invoices_by_project, new_invoice, etc.) remain the same ...
    check_project_permission(project)
    invoices = project.invoices.order_by(Invoice.invoice_date.desc()).all()
    return render_template("invoices/index.html", project=project, invoices=invoices)

@invoice_bp.route("/new/project/<int:project_id>", methods=["GET", "POST"])
@login_required
def new_invoice(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    if request.method == "POST":
        invoice_number = sanitize_input(request.form.get("invoice_number"))
        invoice_date_str = request.form.get("invoice_date")
        contractor_id = request.form.get("contractor_id")
        notes = sanitize_input(request.form.get("notes"))
        if not all([invoice_number, invoice_date_str, contractor_id]):
            flash("رقم المستخلص، التاريخ، والمقاول هي حقول مطلوبة.", "danger")
            return redirect(url_for("invoice.new_invoice", project_id=project_id))
        if Invoice.query.filter_by(invoice_number=invoice_number).first():
            flash("رقم المستخلص هذا موجود بالفعل. الرجاء إدخال رقم فريد.", "danger")
            return redirect(url_for("invoice.new_invoice", project_id=project_id))
        try:
            invoice_date = datetime.datetime.strptime(invoice_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("صيغة التاريخ غير صالحة.", "danger")
            return redirect(url_for("invoice.new_invoice", project_id=project_id))
        new_invoice = Invoice(
            project_id=project.id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            contractor_id=int(contractor_id),
            notes=notes,
            status='جديد'
        )
        db.session.add(new_invoice)
        db.session.commit()
        flash("تم إنشاء المستخلص بنجاح. يمكنك الآن إضافة البنود إليه.", "success")
        return redirect(url_for("invoice.show_invoice", invoice_id=new_invoice.id))
    
    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template("invoices/new.html", project=project, contractors=contractors)

@invoice_bp.route("/<int:invoice_id>/delete", methods=["POST"])
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)
    project_id = invoice.project_id
    if current_user.role != 'admin':
        abort(403)
    db.session.delete(invoice)
    db.session.commit()
    flash(f"تم حذف المستخلص رقم '{invoice.invoice_number}' وكل ما يتعلق به بنجاح.", "success")
    return redirect(url_for("invoice.get_invoices_by_project", project_id=project_id))

@invoice_bp.route("/<int:invoice_id>")
@login_required
def show_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)
    added_main_items_subquery = db.session.query(InvoiceItem.item_id).filter(
        InvoiceItem.invoice_id == invoice.id,
        InvoiceItem.cost_detail_id.is_(None)
    )
    available_items = Item.query.filter(
        Item.project_id == invoice.project_id,
        Item.contractor_id == invoice.contractor_id,
        ~Item.id.in_(added_main_items_subquery)
    ).order_by(Item.item_number).all()
    added_cost_details_subquery = db.session.query(InvoiceItem.cost_detail_id).filter(
        InvoiceItem.invoice_id == invoice.id,
        InvoiceItem.cost_detail_id.isnot(None)
    )
    available_cost_details = CostDetail.query.filter(
        CostDetail.contractor_id == invoice.contractor_id,
        CostDetail.item.has(project_id=invoice.project_id),
        ~CostDetail.id.in_(added_cost_details_subquery)
    ).order_by(CostDetail.id).all()
    return render_template(
        "invoices/show.html", 
        invoice=invoice, 
        available_items=available_items, 
        available_cost_details=available_cost_details
    )

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
    if selected_id_str.startswith('item_'):
        item_id = int(selected_id_str.split('_')[1])
        item = Item.query.get_or_404(item_id)
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

# --- START: COMPLETE REWRITE OF THE add_payment_to_invoice FUNCTION ---
@invoice_bp.route("/<int:invoice_id>/add_payment", methods=["POST"])
@login_required
def add_payment_to_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)

    payment_date_str = request.form.get("payment_date")
    description = sanitize_input(request.form.get("description"))

    if not payment_date_str:
        flash("تاريخ الدفعة حقل مطلوب.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
    
    try:
        payment_date = datetime.datetime.strptime(payment_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        flash("صيغة التاريخ المدخلة غير صالحة.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    distributions = []
    total_payment_amount = 0.0

    # 1. Collect and validate all distributions from the form
    for key, value in request.form.items():
        if key.startswith("dist_item_"):
            try:
                invoice_item_id = int(key.split("_")[-1])
                amount = float(value) if value else 0.0

                if amount > 0:
                    invoice_item = InvoiceItem.query.get(invoice_item_id)
                    if not invoice_item or invoice_item.invoice_id != invoice_id:
                        flash(f"تم العثور على بند غير صالح في الدفعة (ID: {invoice_item_id}).", "danger")
                        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

                    # Check if the amount exceeds the remaining amount for the item
                    if amount > round(invoice_item.remaining_amount, 2) + 0.001: # Add tolerance for float issues
                        flash(f"المبلغ المدفوع للبند '{invoice_item.description[:30]}...' يتجاوز المبلغ المتبقي.", "danger")
                        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

                    distributions.append({'invoice_item': invoice_item, 'amount': amount})
                    total_payment_amount += amount
            
            except (ValueError, TypeError):
                flash("تم إدخال قيمة غير صالحة لأحد البنود.", "danger")
                return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    if not distributions:
        flash("الرجاء إدخال مبلغ لدفعه لبند واحد على الأقل.", "warning")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    # 2. Create the main Payment record and its distributions
    try:
        new_payment = Payment(
            invoice_id=invoice.id,
            amount=total_payment_amount,
            payment_date=payment_date,
            description=description
        )
        db.session.add(new_payment)
        db.session.flush() # Flush to get the ID of the new_payment

        for dist_data in distributions:
            new_distribution = PaymentDistribution(
                payment_id=new_payment.id,
                invoice_item_id=dist_data['invoice_item'].id,
                amount=dist_data['amount']
            )
            db.session.add(new_distribution)

        db.session.commit()
        flash("تم تسجيل الدفعة وتوزيعها بنجاح.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء حفظ الدفعة: {e}", "danger")

    return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
# --- END: COMPLETE REWRITE OF THE add_payment_to_invoice FUNCTION ---

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
        # START: THE FIX - Capture the selected invoice item ID
        invoice_item_id_str = request.form.get("invoice_item_id")
        # END: THE FIX

        if not amount_str or not payment_date_str:
            flash("المبلغ وتاريخ الدفعة حقول مطلوبة.", "danger")
            return redirect(url_for('invoice.edit_payment', payment_id=payment.id))
        
        try:
            payment.amount = float(amount_str)
            payment.payment_date = datetime.datetime.strptime(payment_date_str, "%Y-%m-%d").date()
            payment.description = description
            
            # START: THE FIX - Update the linked item
            if invoice_item_id_str and invoice_item_id_str.isdigit():
                payment.invoice_item_id = int(invoice_item_id_str)
            else:
                payment.invoice_item_id = None # Set to None if no item is selected
            # END: THE FIX
            
            db.session.commit()
            flash("تم تحديث الدفعة بنجاح.", "success")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice.id))
        except (ValueError, TypeError):
            flash("البيانات المدخلة للمبلغ أو التاريخ غير صالحة.", "danger")
    
    # START: THE FIX - Pass the invoice object to the template
    return render_template("invoices/edit_payment.html", payment=payment, invoice=invoice)
    # END: THE FIX

@invoice_bp.route("/payments/<int:payment_id>/delete", methods=["POST"])
@login_required
def delete_payment_from_invoice(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    invoice = payment.invoice
    check_project_permission(invoice.project)
    invoice_id = invoice.id
    db.session.delete(payment)
    db.session.commit()
    flash("تم حذف الدفعة بنجاح.", "success")
    return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

@invoice_bp.route("/items/<int:invoice_item_id>/delete", methods=["POST"])
@login_required
def delete_item_from_invoice(invoice_item_id):
    invoice_item = InvoiceItem.query.get_or_404(invoice_item_id)
    invoice = invoice_item.invoice
    check_project_permission(invoice.project)

    if invoice_item.payments:
        flash("لا يمكن حذف بند تم تسجيل دفعات مرتبطة به مباشرة. يجب حذف الدفعات المرتبطة بهذا البند أولاً.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice.id))
    
    invoice_id = invoice.id
    db.session.delete(invoice_item)
    db.session.commit()
    flash("تم حذف البند من المستخلص بنجاح.", "success")
    return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

@invoice_bp.route("/items/<int:invoice_item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item_from_invoice(invoice_item_id):
    invoice_item = InvoiceItem.query.get_or_404(invoice_item_id)
    invoice = invoice_item.invoice
    check_project_permission(invoice.project)

    if invoice_item.payments:
        flash("لا يمكن تعديل كمية بند تم تسجيل دفعات مرتبطة به مباشرة.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice.id))

    if request.method == "POST":
        quantity_str = request.form.get("quantity")
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                flash("يجب أن تكون الكمية أكبر من صفر.", "danger")
                return redirect(url_for('invoice.edit_item_from_invoice', invoice_item_id=invoice_item.id))
            
            invoice_item.quantity = quantity
            invoice_item.total_price = quantity * invoice_item.unit_price
            
            db.session.commit()
            flash("تم تحديث كمية البند بنجاح.", "success")
            return redirect(url_for('invoice.show_invoice', invoice_id=invoice.id))
        except (ValueError, TypeError):
            flash("الكمية المدخلة غير صالحة.", "danger")
    
    return render_template("invoices/edit_invoice_item.html", invoice_item=invoice_item)




