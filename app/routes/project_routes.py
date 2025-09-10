from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from app.models.project import Project
from app.models.item import Item
from app.models.user import User
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission
from app.forms import ProjectForm
from sqlalchemy.orm import selectinload, undefer


project_bp = Blueprint("project", __name__)

@project_bp.route("/projects")
@login_required
def get_projects():
    show_archived = request.args.get('show_archived', 'false').lower() == 'true'

    # The query is now much simpler
    query = Project.query

    if current_user.role not in ['admin', 'sub-admin']:
        query = query.join(Project.users).filter(User.id == current_user.id)

    if show_archived:
        query = query.filter(Project.is_archived == True)
    else:
        query = query.filter(Project.is_archived == False)
    
    # We use joinedload to prevent multiple queries for items later
    # Use selectinload for better performance on one-to-many relationships
    # and undefer to explicitly load our calculated property
    projects = query.options(
        selectinload(Project.items).undefer(Item.actual_details_cost)
    ).all()    
    return render_template("projects/index.html", projects=projects, show_archived=show_archived)


@project_bp.route("/projects/<int:project_id>")
@login_required
def get_project(project_id):
    # Eagerly load items and their cost details to optimize performance
    project = Project.query.options(
        joinedload(Project.items).joinedload(Item.cost_details)
    ).get_or_404(project_id)
    
    check_project_permission(project)
    
    # The cost properties are now accessed directly from the project object
    # These calculations are specific to the view and can remain here
    if not project.items:
        project.completion_percentage = 0.0
    else:
        completed_items = sum(1 for item in project.items if item.status == 'مكتمل')
        project.completion_percentage = (completed_items / len(project.items)) * 100 if project.items else 0.0

    if project.total_actual_cost == 0:
        project.financial_completion_percentage = 0.0
    else:
        project.financial_completion_percentage = (project.total_paid_amount / project.total_actual_cost) * 100

    return render_template("projects/show.html", project=project)


@project_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    if current_user.role not in ['admin', 'sub-admin']:
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
    if current_user.role not in ['admin', 'sub-admin']:
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
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
        
    db.session.delete(project)
    db.session.commit()
    flash("تم حذف المشروع بنجاح!", "success")
    return redirect(url_for("project.get_projects"))


@project_bp.route("/projects/<int:project_id>/toggle-archive", methods=["POST"])
@login_required
def toggle_archive(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role not in ['admin', 'sub-admin']:
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
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
    return redirect(url_for('project.get_projects'))
    
@project_bp.route("/summary")
@login_required
def projects_summary():
    """
    يعرض صفحة ملخص مالي لجميع المشاريع.
    """
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)

    projects = Project.query.filter_by(is_archived=False).all()
    
    grand_totals = {
        'contract_cost': sum(p.total_contract_cost for p in projects),
        'actual_cost': sum(p.total_actual_cost for p in projects),
        'paid_amount': sum(p.total_paid_amount for p in projects),
        'remaining_amount': sum(p.total_remaining_amount for p in projects),
    }

    return render_template("projects/summary.html", projects=projects, totals=grand_totals)