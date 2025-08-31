from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from app.models.contractor import Contractor
from app.models.project import Project
from app.models.user import User 
from app.models.invoice import Invoice
from app.extensions import db
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.utils import sanitize_input

contractor_bp = Blueprint("contractor", __name__, url_prefix='/contractors')

@contractor_bp.route("/")
@login_required
def get_contractors():
    """عرض قائمة بجميع المقاولين"""
    if current_user.role != 'admin':
        allowed_project_ids = [p.id for p in current_user.projects]
        if not allowed_project_ids:
            contractors = []
        else:
            contractors = Contractor.query.join(Invoice).join(Project).filter(
                Project.id.in_(allowed_project_ids)
            ).distinct().order_by(Contractor.name).all()
    else:
        contractors = Contractor.query.order_by(Contractor.name).all()
    
    return render_template("contractors/index.html", contractors=contractors)

@contractor_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_contractor():
    if current_user.role != 'admin':
        abort(403)
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        contact_person = sanitize_input(request.form.get('contact_person'))
        phone = sanitize_input(request.form.get('phone'))
        email = sanitize_input(request.form.get('email'))
        notes = sanitize_input(request.form.get('notes'))

        if not name:
            flash('اسم المقاول هو حقل مطلوب.', 'danger')
            return redirect(url_for('contractor.new_contractor'))

        if Contractor.query.filter_by(name=name).first():
            flash('مقاول بنفس هذا الاسم موجود بالفعل.', 'danger')
            return redirect(url_for('contractor.new_contractor'))

        new_contractor = Contractor(
            name=name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            notes=notes
        )
        db.session.add(new_contractor)
        db.session.commit()
        flash('تمت إضافة المقاول بنجاح!', 'success')
        return redirect(url_for('contractor.get_contractors'))
    
    return render_template("contractors/new.html")

# --- START: New Edit Contractor Function ---
@contractor_bp.route("/<int:contractor_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_contractor(contractor_id):
    if current_user.role != 'admin':
        abort(403)
    
    contractor = Contractor.query.get_or_404(contractor_id)
    
    if request.method == 'POST':
        new_name = sanitize_input(request.form.get('name'))
        
        # Check if new name already exists for another contractor
        if new_name != contractor.name and Contractor.query.filter_by(name=new_name).first():
            flash('مقاول آخر بنفس هذا الاسم موجود بالفعل.', 'danger')
            return redirect(url_for('contractor.edit_contractor', contractor_id=contractor_id))

        contractor.name = new_name
        contractor.contact_person = sanitize_input(request.form.get('contact_person'))
        contractor.phone = sanitize_input(request.form.get('phone'))
        contractor.email = sanitize_input(request.form.get('email'))
        contractor.notes = sanitize_input(request.form.get('notes'))
        
        db.session.commit()
        flash('تم تحديث بيانات المقاول بنجاح!', 'success')
        return redirect(url_for('contractor.get_contractors'))

    return render_template("contractors/edit.html", contractor=contractor)
# --- END: New Edit Contractor Function ---

# --- START: New Delete Contractor Function ---
@contractor_bp.route("/<int:contractor_id>/delete", methods=['POST'])
@login_required
def delete_contractor(contractor_id):
    if current_user.role != 'admin':
        abort(403)
        
    contractor = Contractor.query.get_or_404(contractor_id)
    
    # Safety check: Prevent deletion if contractor is linked to any invoices
    if contractor.invoices.first():
        flash('لا يمكن حذف هذا المقاول لوجود مستخلصات مرتبطة به. يجب حذف المستخلصات أولاً.', 'danger')
        return redirect(url_for('contractor.get_contractors'))
        
    db.session.delete(contractor)
    db.session.commit()
    flash(f"تم حذف المقاول '{contractor.name}' بنجاح.", "success")
    return redirect(url_for('contractor.get_contractors'))
# --- END: New Delete Contractor Function ---

@contractor_bp.route("/<int:contractor_id>")
@login_required
def show_contractor(contractor_id):
    contractor = Contractor.query.get_or_404(contractor_id)
    
    invoices_query = Invoice.query.filter_by(contractor_id=contractor_id)

    project_filter = request.args.get('project_id', type=int)
    search_filter = request.args.get('search', '')

    if project_filter:
        invoices_query = invoices_query.filter(Invoice.project_id == project_filter)
    
    if search_filter:
        search_term = f"%{search_filter}%"
        invoices_query = invoices_query.filter(Invoice.invoice_number.ilike(search_term))
    
    invoices = invoices_query.order_by(Invoice.invoice_date.desc()).all()
    
    total_due = sum(inv.total_amount for inv in invoices if inv.status != 'ملغي')
    total_paid = sum(inv.paid_amount for inv in invoices if inv.status != 'ملغي')
    remaining = total_due - total_paid

    projects_query = Project.query.join(Invoice).filter(Invoice.contractor_id == contractor_id)
    if current_user.role != 'admin':
        projects_query = projects_query.join(Project.users).filter(User.id == current_user.id)
    projects = projects_query.distinct().order_by(Project.name).all()

    return render_template(
        "contractors/show.html", 
        contractor=contractor, 
        invoices=invoices,
        projects=projects,
        total_due=total_due,
        total_paid=total_paid,
        remaining=remaining,
        filters={'project_id': project_filter, 'search': search_filter}
    )
