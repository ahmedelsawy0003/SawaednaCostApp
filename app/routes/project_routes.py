from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from app.models.project import Project
from app.models.item import Item
from app.models.user import User # <<< Add this import
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input

project_bp = Blueprint("project", __name__)

@project_bp.route("/projects")
@login_required
def get_projects():
    if current_user.role == 'admin':
        projects = Project.query.all()
    else:
        projects = current_user.projects
    return render_template("projects/index.html", projects=projects)

@project_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    if current_user.role != 'admin':
        abort(403)

    if request.method == "POST":
        name = sanitize_input(request.form["name"])
        location = sanitize_input(request.form["location"])
        notes = sanitize_input(request.form["notes"])
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        status = request.form["status"]
        spreadsheet_id = request.form.get("spreadsheet_id")
        manager_id = request.form.get("manager_id") # <<< Get manager_id

        new_project = Project(name=name, location=location, start_date=start_date, 
                              end_date=end_date, status=status, notes=notes,
                              spreadsheet_id=spreadsheet_id)
        
        # <<< Assign manager if selected
        if manager_id:
            new_project.manager_id = int(manager_id)
        
        db.session.add(new_project)
        db.session.commit()
        flash("تم إضافة المشروع بنجاح!", "success")
        return redirect(url_for("project.get_projects"))
    
    # START: Fetch users for the dropdown
    users = User.query.all()
    return render_template("projects/new.html", users=users)
    # END: Fetch users

@project_bp.route("/projects/<int:project_id>")
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    return render_template("projects/show.html", project=project)

@project_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role != 'admin':
        abort(403)
    
    if request.method == "POST":
        project.name = sanitize_input(request.form["name"])
        project.location = sanitize_input(request.form["location"])
        project.notes = sanitize_input(request.form["notes"])
        project.start_date = request.form["start_date"]
        project.end_date = request.form["end_date"]
        project.status = request.form["status"]
        project.spreadsheet_id = request.form.get("spreadsheet_id")
        
        # <<< Update manager_id
        manager_id = request.form.get("manager_id")
        project.manager_id = int(manager_id) if manager_id else None

        db.session.commit()
        flash("تم تحديث المشروع بنجاح!", "success")
        return redirect(url_for("project.get_project", project_id=project.id))

    # START: Fetch users for the dropdown
    users = User.query.all()
    return render_template("projects/edit.html", project=project, users=users)
    # END: Fetch users

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

# ... (The rest of the file remains the same) ...
@project_bp.route("/projects/<int:project_id>/dashboard")
@login_required
def project_dashboard(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    items = Item.query.filter_by(project_id=project.id).all()

    contract_costs = [item.contract_total_cost for item in items]
    actual_costs = [item.actual_total_cost for item in items if item.actual_total_cost is not None]
    item_descriptions = [item.description for item in items]

    chart_data = {
        "labels": item_descriptions,
        "datasets": [
            {
                "label": "التكلفة التعاقدية",
                "data": contract_costs,
                "backgroundColor": "rgba(54, 162, 235, 0.6)"
            },
            {
                "label": "التكلفة الفعلية",
                "data": actual_costs,
                "backgroundColor": "rgba(255, 99, 132, 0.6)"
            }
        ]
    }

    return render_template("projects/dashboard.html", project=project, chart_data=chart_data)

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