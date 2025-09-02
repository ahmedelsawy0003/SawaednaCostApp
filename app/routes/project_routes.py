from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy.orm import joinedload
from sqlalchemy import func, case
from app.models.project import Project
from app.models.user import User, user_project_association
from app.models.item import Item
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem 
from app.models.payment import Payment
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input
from app.forms import ProjectForm

project_bp = Blueprint("project", __name__)

@project_bp.route("/projects")
@login_required
def get_projects():
    show_archived = request.args.get('show_archived', 'false').lower() == 'true'

    # --- START: THE FIX ---
    # Subquery for paid amounts remains the same
    paid_subquery = db.session.query(
        Invoice.project_id,
        func.sum(Payment.amount).label('total_paid')
    ).join(Payment).group_by(Invoice.project_id).subquery()

    # Main query is now simplified to sum the manual actual costs directly
    query = db.session.query(
        Project,
        func.coalesce(func.sum(Item.contract_quantity * Item.contract_unit_cost), 0).label('total_contract_cost'),
        func.coalesce(func.sum(Item.actual_quantity * Item.actual_unit_cost), 0).label('total_actual_cost'),
        func.coalesce(paid_subquery.c.total_paid, 0).label('total_paid_amount')
    ).outerjoin(Item).outerjoin(paid_subquery, Project.id == paid_subquery.c.project_id).group_by(Project.id, paid_subquery.c.total_paid)
    # --- END: THE FIX ---

    if current_user.role != 'admin':
        query = query.join(user_project_association).filter(user_project_association.c.user_id == current_user.id)

    if show_archived:
        query = query.filter(Project.is_archived == True)
    else:
        query = query.filter(Project.is_archived == False)

    results = query.all()
    
    projects_with_costs = []
    for project, total_contract, total_actual, total_paid in results:
        project.total_contract_cost = total_contract
        project.total_actual_cost = total_actual
        project.total_paid_amount = total_paid
        project.total_savings = total_contract - total_actual
        project.total_remaining_amount = total_actual - total_paid
        projects_with_costs.append(project)
        
    return render_template("projects/index.html", projects=projects_with_costs, show_archived=show_archived)

@project_bp.route("/projects/<int:project_id>")
@login_required
def get_project(project_id):
    project = Project.query.options(joinedload(Project.items)).get_or_404(project_id)
    check_project_permission(project)
    
    items = project.items
    project.total_contract_cost = sum(item.contract_total_cost for item in items)
    # This now uses the corrected logic from the item model
    project.total_actual_cost = sum(item.actual_total_cost for item in items if item.actual_total_cost is not None)
    project.total_paid_amount = db.session.query(func.sum(Payment.amount)).join(Invoice).filter(Invoice.project_id == project.id).scalar() or 0.0
    project.total_savings = project.total_contract_cost - project.total_actual_cost
    project.total_remaining_amount = project.total_actual_cost - project.total_paid_amount
    
    if not items:
        project.completion_percentage = 0.0
    else:
        completed_items = sum(1 for item in items if item.status == 'مكتمل')
        project.completion_percentage = (completed_items / len(items)) * 100 if len(items) > 0 else 0.0

    if project.total_actual_cost == 0:
        project.financial_completion_percentage = 0.0
    else:
        project.financial_completion_percentage = (project.total_paid_amount / project.total_actual_cost) * 100

    return render_template("projects/show.html", project=project)

@project_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    if current_user.role != 'admin':
        abort(403)
    
    form = ProjectForm()
    form.manager_id.choices = [(user.id, user.username) for user in User.query.order_by('username').all()]
    form.manager_id.choices.insert(0, (0, '-- اختر مديرًا للمشروع --'))

    if form.validate_on_submit():
        manager_id_val = form.manager_id.data
        new_project = Project(
            name=form.name.data,
            location=form.location.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            notes=form.notes.data,
            spreadsheet_id=form.spreadsheet_id.data,
            manager_id=manager_id_val if manager_id_val != 0 else None
        )
        
        db.session.add(new_project)
        db.session.commit()
        flash("تم إضافة المشروع بنجاح!", "success")
        return redirect(url_for("project.get_projects"))
    
    return render_template("projects/new.html", form=form)

@project_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin':
        abort(403)
    
    form = ProjectForm(obj=project)
    form.manager_id.choices = [(user.id, user.username) for user in User.query.order_by('username').all()]
    form.manager_id.choices.insert(0, (0, '-- اختر مديرًا للمشروع --'))

    if form.validate_on_submit():
        manager_id_val = form.manager_id.data
        project.name = form.name.data
        project.location = form.location.data
        project.notes = form.notes.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.status = form.status.data
        project.spreadsheet_id = form.spreadsheet_id.data
        project.manager_id = manager_id_val if manager_id_val != 0 else None

        db.session.commit()
        flash("تم تحديث المشروع بنجاح!", "success")
        return redirect(url_for("project.get_project", project_id=project.id))

    if request.method == 'GET':
        form.manager_id.data = project.manager_id

    return render_template("projects/edit.html", form=form, project=project)

@project_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin':
        abort(403)
        
    db.session.delete(project)
    db.session.commit()
    flash("تم حذف المشروع بنجاح!", "success")
    return redirect(url_for("project.get_projects"))

@project_bp.route("/projects/<int:project_id>/toggle-archive", methods=["POST"])
@login_required
def toggle_archive(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin':
        abort(403)
    
    project.is_archived = not project.is_archived
    db.session.commit()

    if project.is_archived:
        flash(f"تمت أرشفة المشروع '{project.name}' بنجاح.", "success")
    else:
        flash(f"تم إلغاء أرشفة المشروع '{project.name}' بنجاح.", "info")
        
    show_archived = request.args.get('show_archived', 'false')
    return redirect(url_for("project.get_projects", show_archived=show_archived))

@project_bp.route("/projects/<int:project_id>/dashboard")
@login_required
def project_dashboard(project_id):
    return redirect(url_for('project.get_project', project_id=project_id))

@project_bp.route("/dashboard")
@login_required
def all_projects_dashboard():
    if current_user.role != 'admin':
        abort(403)
    return redirect(url_for('project.get_projects'))
