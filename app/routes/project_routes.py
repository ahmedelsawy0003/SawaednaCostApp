from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from app.models.project import Project
from app.models.user import User 
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input
# --- START: إضافة استيراد النموذج ---
from app.forms import ProjectForm
# --- END: إضافة استيراد النموذج ---

project_bp = Blueprint("project", __name__)

@project_bp.route("/projects")
@login_required
def get_projects():
    show_archived = request.args.get('show_archived', 'false').lower() == 'true'
    
    query = Project.query
    if current_user.role != 'admin':
        query = query.join(User.projects).filter(User.id == current_user.id)

    if show_archived:
        projects = query.filter(Project.is_archived == True).all()
    else:
        projects = query.filter(Project.is_archived == False).all()
        
    return render_template("projects/index.html", projects=projects, show_archived=show_archived)

# --- START: تعديل دالة إضافة مشروع جديد ---
@project_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    if current_user.role != 'admin':
        abort(403)
    
    form = ProjectForm()

    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
            location=form.location.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            notes=form.notes.data,
            spreadsheet_id=form.spreadsheet_id.data,
            manager=form.manager.data # WTForms-SQLAlchemy يعيد الكائن (object) مباشرة
        )
        
        db.session.add(new_project)
        db.session.commit()
        flash("تم إضافة المشروع بنجاح!", "success")
        return redirect(url_for("project.get_projects"))
    
    return render_template("projects/new.html", form=form)
# --- END: تعديل دالة إضافة مشروع جديد ---

@project_bp.route("/projects/<int:project_id>")
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    return render_template("projects/show.html", project=project)

# --- START: تعديل دالة تعديل المشروع ---
@project_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin':
        abort(403)
    
    # عند التعديل، نمرر كائن المشروع للنموذج ليقوم بتعبئة الحقول بالبيانات الحالية
    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        # تحديث بيانات المشروع من النموذج
        project.name = form.name.data
        project.location = form.location.data
        project.notes = form.notes.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.status = form.status.data
        project.spreadsheet_id = form.spreadsheet_id.data
        project.manager = form.manager.data

        db.session.commit()
        flash("تم تحديث المشروع بنجاح!", "success")
        return redirect(url_for("project.get_project", project_id=project.id))

    return render_template("projects/edit.html", form=form, project=project)
# --- END: تعديل دالة تعديل المشروع ---


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
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    return render_template("projects/dashboard.html", project=project)

@project_bp.route("/projects/<int:project_id>/summary")
@login_required
def project_summary(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    return jsonify({
        "total_contract_cost": project.total_contract_cost,
        "total_actual_cost": project.total_actual_cost,
        "total_savings": project.total_savings,
        "completion_percentage": project.completion_percentage,
        "financial_completion_percentage": project.financial_completion_percentage
    })

@project_bp.route("/dashboard")
@login_required
def all_projects_dashboard():
    if current_user.role != 'admin':
        abort(403)
    projects = Project.query.all()
    
    total_contract_cost_all = sum(p.total_contract_cost for p in projects)
    total_actual_cost_all = sum(p.total_actual_cost for p in projects)
    total_savings_all = sum(p.total_savings for p in projects)
    total_paid_amount_all = sum(p.total_paid_amount for p in projects)
    total_remaining_amount_all = sum(p.total_remaining_amount for p in projects)

    status_counts = {}
    for project in projects:
        status_counts[project.status] = status_counts.get(project.status, 0) + 1

    status_labels = list(status_counts.keys())
    status_data = list(status_counts.values())

    return render_template(
        "projects/all_projects_dashboard.html",
        projects=projects,
        total_contract_cost_all=total_contract_cost_all,
        total_actual_cost_all=total_actual_cost_all,
        total_savings_all=total_savings_all,
        total_paid_amount_all=total_paid_amount_all,
        total_remaining_amount_all=total_remaining_amount_all,
        status_labels=status_labels,
        status_data=status_data
    )