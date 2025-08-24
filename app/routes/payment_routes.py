from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.payment import Payment
from app.models.project import Project
from app.models.item import Item
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission # <<< Import the function

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/projects/<int:project_id>/payments")
@login_required
def get_payments(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project) # <<< Add permission check
    payments = Payment.query.filter_by(project_id=project_id).order_by(Payment.payment_date.desc()).all()
    return render_template("payments/index.html", project=project, payments=payments)

@payment_bp.route("/projects/<int:project_id>/payments/new", methods=["GET", "POST"])
@login_required
def new_payment(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project) # <<< Add permission check
    items = Item.query.filter_by(project_id=project_id).all()
    if request.method == "POST":
        amount = float(request.form["amount"])
        payment_date = request.form["payment_date"]
        description = request.form.get("description")
        item_id = request.form.get("item_id")

        new_payment = Payment(project_id=project_id, amount=amount, payment_date=payment_date, description=description)
        if item_id and item_id != ":":
            new_payment.item_id = int(item_id)
        
        db.session.add(new_payment)
        db.session.commit()
        flash("تم إضافة الدفعة بنجاح!", "success")
        return redirect(url_for("payment.get_payments", project_id=project_id))
    return render_template("payments/new.html", project=project, items=items)

@payment_bp.route("/payments/<int:payment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    project = payment.project
    check_project_permission(project) # <<< Add permission check
    items = Item.query.filter_by(project_id=project.id).all()

    if request.method == "POST":
        payment.amount = float(request.form["amount"])
        payment.payment_date = request.form["payment_date"]
        payment.description = request.form.get("description")
        item_id = request.form.get("item_id")
        payment.item_id = int(item_id) if item_id and item_id != ":" else None
        
        db.session.commit()
        flash("تم تحديث الدفعة بنجاح!", "success")
        return redirect(url_for("payment.get_payments", project_id=payment.project_id))
    return render_template("payments/edit.html", payment=payment, project=project, items=items)

@payment_bp.route("/payments/<int:payment_id>/delete", methods=["POST"])
@login_required
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    check_project_permission(payment.project) # <<< Add permission check
    project_id = payment.project_id
    db.session.delete(payment)
    db.session.commit()
    flash("تم حذف الدفعة بنجاح!", "success")
    return redirect(url_for("payment.get_payments", project_id=project_id))