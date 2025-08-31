from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from sqlalchemy import func # <<< تأكد من استيراد func
from app.models.project import Project
from app.models.contractor import Contractor
from app.models.item import Item
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input
import datetime

# Blueprint
invoice_bp = Blueprint("invoice", __name__, url_prefix='/invoices')

# ... (get_invoices_by_project, new_invoice, delete_invoice, show_invoice remain the same) ...
@invoice_bp.route("/project/<int:project_id>")
@login_required
def get_invoices_by_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    invoices = project.invoices.order_by(Invoice.invoice_date.desc()).all()
    return render_template("invoices/index.html", project=project, invoices=invoices)

@invoice_bp.route("/project/<int:project_id>/new", methods=["GET", "POST"])
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
    subquery = db.session.query(InvoiceItem.item_id).filter(InvoiceItem.invoice_id == invoice.id)
    available_items = Item.query.filter(
        Item.project_id == invoice.project_id,
        Item.contractor_id == invoice.contractor_id,
        ~Item.id.in_(subquery)
    ).order_by(Item.item_number).all()
    return render_template("invoices/show.html", invoice=invoice, available_items=available_items)


# --- START: التعديل الجوهري وإضافة شرط التحقق من الكمية ---
@invoice_bp.route("/<int:invoice_id>/add_item", methods=["POST"])
@login_required
def add_item_to_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)
    item_id = request.form.get("item_id")
    quantity_str = request.form.get("quantity")

    # 1. التحقق الأساسي من المدخلات
    if not item_id or not quantity_str:
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

    item = Item.query.get_or_404(item_id)

    # 2. التحقق من وجود كمية فعلية مسجلة في البند الرئيسي
    max_quantity = item.actual_quantity
    if max_quantity is None or max_quantity <= 0:
        flash(f"لا يمكن إضافة البند '{item.item_number}' للمستخلص لعدم وجود 'كمية فعلية' مسجلة له في صفحة البنود.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    # 3. حساب الكمية التي تمت فوترتها مسبقاً في المستخلصات الأخرى
    previously_invoiced_qty = db.session.query(
        func.sum(InvoiceItem.quantity)
    ).filter(
        InvoiceItem.item_id == item.id,
        InvoiceItem.invoice_id != invoice.id  # استثناء المستخلص الحالي
    ).scalar() or 0.0

    # 4. تطبيق الشرط الرئيسي
    if (previously_invoiced_qty + new_quantity) > max_quantity:
        remaining_qty = max_quantity - previously_invoiced_qty
        flash(f"لا يمكن إضافة هذه الكمية. الكمية القصوى المسموح بها لهذا البند هي {max_quantity}. تمت فوترة {previously_invoiced_qty} مسبقاً. الكمية المتبقية المتاحة هي {remaining_qty:.2f} فقط.", "danger")
        return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))

    # 5. إذا نجحت كل الشروط، قم بإضافة البند للمستخلص
    new_invoice_item = InvoiceItem(item=item, quantity=new_quantity)
    new_invoice_item.invoice_id = invoice.id
    db.session.add(new_invoice_item)
    db.session.commit()
    flash(f"تمت إضافة البند '{item.item_number}' إلى المستخلص بنجاح.", "success")
    return redirect(url_for('invoice.show_invoice', invoice_id=invoice_id))
# --- END: التعديل الجوهري ---


# ... (باقي الدوال في الملف تبقى كما هي بدون تغيير) ...
@invoice_bp.route("/<int:invoice_id>/add_payment", methods=["POST"])
@login_required
def add_payment_to_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    check_project_permission(invoice.project)
    amount_str = request.form.get("amount")
    payment_date_str = request.form.get("payment_date")
    description = sanitize_input(request.form.get("description"))
    invoice_item_id = request.form.get("invoice_item_id") # Get the selected item

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
    if invoice.payments:
        flash("لا يمكن حذف بنود من مستخلص تم تسجيل دفعات له. يجب حذف الدفعات أولاً.", "danger")
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

    if invoice.payments:
        flash("لا يمكن تعديل بنود مستخلص تم تسجيل دفعات له.", "danger")
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