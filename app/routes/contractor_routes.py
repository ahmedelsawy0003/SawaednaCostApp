from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from app.models.contractor import Contractor
from app.models.cost_detail import CostDetail
from app.models.project import Project
from app.models.user import User 
from app.models.item import Item # <<< أضف هذا السطر
from app.extensions import db
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.utils import sanitize_input

contractor_bp = Blueprint("contractor", __name__, url_prefix='/contractors')

@contractor_bp.route("/")
@login_required
def get_contractors():
    """عرض قائمة بجميع المقاولين"""
    query = Contractor.query.join(CostDetail, isouter=True).join(Item, isouter=True)

    if current_user.role != 'admin':
        allowed_project_ids = [p.id for p in current_user.projects]
        if not allowed_project_ids:
            contractors = []
        else:
            query = query.filter(Item.project_id.in_(allowed_project_ids))
            contractors = query.distinct().order_by(Contractor.name).all()
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
    """عرض صفحة تفصيلية للمقاول مع جميع تفاصيل التكاليف والدفعات المرتبطة به"""
    contractor = Contractor.query.get_or_404(contractor_id)

    projects_query = Project.query.join(Project.items).join(Item.cost_details).filter(CostDetail.contractor_id == contractor_id)
    if current_user.role != 'admin':
        projects_query = projects_query.join(Project.users).filter(User.id == current_user.id)
    
    projects = projects_query.distinct().all()
    project_filter = request.args.get('project_id', type=int)
    search_filter = request.args.get('search', '')
    cost_details_query = CostDetail.query.filter_by(contractor_id=contractor_id).join(CostDetail.item) # join with item to search

    if project_filter:
        cost_details_query = cost_details_query.filter(Item.project_id == project_filter)
    
    if search_filter:
        search_term = f"%{search_filter}%"
        cost_details_query = cost_details_query.filter(
            or_(
                CostDetail.description.ilike(search_term),
                Item.item_number.ilike(search_term)
            )
        )
    
    cost_details = cost_details_query.all()
    
    total_due = sum(cd.total_cost for cd in cost_details if cd.total_cost)
    total_paid = sum(cd.total_paid for cd in cost_details)
    remaining = total_due - total_paid

    return render_template(
        "contractors/show.html", 
        contractor=contractor, 
        cost_details=cost_details,
        projects=projects,
        total_due=total_due,
        total_paid=total_paid,
        remaining=remaining,
        filters={'project_id': project_filter, 'search': search_filter}
    )