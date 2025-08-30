from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from app.models.contractor import Contractor
from app.models.cost_detail import CostDetail
from app.models.project import Project
from app.models.user import User 
from app.models.item import Item 
from app.models.invoice import Invoice # Import the Invoice model
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
            # This logic can be improved, but let's keep it for now
            items_query = Item.query.filter(Item.project_id.in_(allowed_project_ids))
            contractor_ids = {item.contractor_id for item in items_query if item.contractor_id}
            
            cost_details_query = CostDetail.query.join(Item).filter(Item.project_id.in_(allowed_project_ids))
            for detail in cost_details_query:
                if detail.contractor_id:
                    contractor_ids.add(detail.contractor_id)

            contractors = Contractor.query.filter(Contractor.id.in_(list(contractor_ids))).order_by(Contractor.name).all()
    else:
        contractors = Contractor.query.order_by(Contractor.name).all()
    
    return render_template("contractors/index.html", contractors=contractors)


@contractor_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_contractor():
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


@contractor_bp.route("/<int:contractor_id>")
@login_required
def show_contractor(contractor_id):
    """عرض صفحة تفصيلية للمقاول مع المستخلصات والأعمال المرتبطة به"""
    contractor = Contractor.query.get_or_404(contractor_id)

    # --- START: New logic based on invoices ---
    
    # Base query for invoices related to this contractor
    invoices_query = Invoice.query.filter_by(contractor_id=contractor_id)

    # --- Filtering Logic ---
    project_filter = request.args.get('project_id', type=int)
    search_filter = request.args.get('search', '')

    if project_filter:
        invoices_query = invoices_query.filter(Invoice.project_id == project_filter)
    
    if search_filter:
        search_term = f"%{search_filter}%"
        invoices_query = invoices_query.filter(Invoice.invoice_number.ilike(search_term))
    
    invoices = invoices_query.order_by(Invoice.invoice_date.desc()).all()
    
    # --- Financial Summary Calculation ---
    total_due = sum(inv.total_amount for inv in invoices if inv.status != 'ملغي')
    total_paid = sum(inv.paid_amount for inv in invoices if inv.status != 'ملغي')
    remaining = total_due - total_paid

    # Fetch distinct projects for the filter dropdown
    projects_query = Project.query.join(Invoice).filter(Invoice.contractor_id == contractor_id)
    if current_user.role != 'admin':
        projects_query = projects_query.join(Project.users).filter(User.id == current_user.id)
    projects = projects_query.distinct().order_by(Project.name).all()

    # --- END: New logic based on invoices ---

    return render_template(
        "contractors/show.html", 
        contractor=contractor, 
        invoices=invoices, # Pass invoices instead of items
        projects=projects,
        total_due=total_due,
        total_paid=total_paid,
        remaining=remaining,
        filters={'project_id': project_filter, 'search': search_filter}
    )