from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from app.models.contractor import Contractor
from app.models.cost_detail import CostDetail
from app.models.project import Project
from app.models.user import User 
from app.models.item import Item 
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
            contractors_from_items = db.session.query(Contractor).join(Item).filter(Item.project_id.in_(allowed_project_ids)).distinct()
            contractors_from_details = db.session.query(Contractor).join(CostDetail).join(Item).filter(Item.project_id.in_(allowed_project_ids)).distinct()
            
            all_contractors = list(set(contractors_from_items.all() + contractors_from_details.all()))
            contractors = sorted(all_contractors, key=lambda c: c.name)
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
    """عرض صفحة تفصيلية للمقاول مع جميع البنود والأعمال المرتبطة به"""
    contractor = Contractor.query.get_or_404(contractor_id)

    # -- START: Corrected logic to fetch ITEMS associated with the contractor --
    # 1. Subquery to find item IDs where a cost_detail is assigned to this contractor
    subquery = db.session.query(Item.id).join(CostDetail).filter(CostDetail.contractor_id == contractor_id).distinct()

    # 2. Main query for Items
    items_query = Item.query.filter(
        or_(
            Item.contractor_id == contractor_id,
            Item.id.in_(subquery)
        )
    )
    # -- END: Corrected logic --

    # --- Filtering Logic ---
    projects_query = Project.query.join(Project.items).filter(Item.id.in_([i.id for i in items_query.all()]))
    if current_user.role != 'admin':
        projects_query = projects_query.join(Project.users).filter(User.id == current_user.id)
    projects = projects_query.distinct().all()

    project_filter = request.args.get('project_id', type=int)
    search_filter = request.args.get('search', '')

    if project_filter:
        items_query = items_query.filter(Item.project_id == project_filter)
    
    if search_filter:
        search_term = f"%{search_filter}%"
        items_query = items_query.filter(
            or_(
                Item.description.ilike(search_term),
                Item.item_number.ilike(search_term)
            )
        )
    
    items = items_query.order_by(Item.project_id, Item.item_number).all()
    
    # --- Recalculate financial summary ---
    total_due = 0
    total_paid = 0
    
    for item in items:
        # If the whole item is assigned to the contractor, sum all its costs
        if item.contractor_id == contractor_id:
            total_due += item.actual_total_cost
            for detail in item.cost_details:
                 total_paid += detail.total_paid
        # Otherwise, only sum costs from details assigned to the contractor
        else:
            for detail in item.cost_details:
                if detail.contractor_id == contractor_id:
                    total_due += detail.total_cost if detail.total_cost else 0
                    total_paid += detail.total_paid

    remaining = total_due - total_paid

    return render_template(
        "contractors/show.html", 
        contractor=contractor, 
        items=items,
        projects=projects,
        total_due=total_due,
        total_paid=total_paid,
        remaining=remaining,
        filters={'project_id': project_filter, 'search': search_filter}
    )