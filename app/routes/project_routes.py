from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models.project import Project
from app.extensions import db

project_bp = Blueprint('project', __name__, url_prefix='/projects')

@project_bp.route('/', methods=['GET'])
def get_projects():
    """الحصول على قائمة المشاريع"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    # تم التعديل هنا: نمرر قائمة الكائنات الأصلية مباشرة
    return render_template('projects/index.html', projects=projects)

@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """الحصول على مشروع محدد"""
    project = Project.query.get_or_404(project_id)
    # تم التعديل هنا: نمرر كائن المشروع الأصلي مباشرة
    return render_template('projects/show.html', project=project)

@project_bp.route('/new', methods=['GET'])
def new_project():
    """عرض نموذج إنشاء مشروع جديد"""
    return render_template('projects/new.html')

@project_bp.route('/', methods=['POST'])
def create_project():
    """إنشاء مشروع جديد"""
    data = request.form
    
    # التحقق من البيانات المطلوبة
    if not data.get('name') or not data.get('manager') or not data.get('location'):
        return jsonify({'error': 'يجب توفير اسم المشروع ومدير المشروع والموقع'}), 400
    
    # إنشاء مشروع جديد
    project = Project(
        name=data.get('name'),
        manager=data.get('manager'),
        location=data.get('location'),
        spreadsheet_id=data.get('spreadsheet_id')
    )
    
    # حفظ المشروع في قاعدة البيانات
    db.session.add(project)
    db.session.commit()
    
    # إذا كان الطلب من واجهة API
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(project.to_dict()), 201
    
    # إعادة التوجيه إلى صفحة المشروع
    return redirect(url_for('project.get_project', project_id=project.id))

@project_bp.route('/<int:project_id>/edit', methods=['GET'])
def edit_project(project_id):
    """عرض نموذج تعديل المشروع"""
    project = Project.query.get_or_404(project_id)
    # هذا السطر كان صحيحاً بالفعل، وأبقينا عليه كما هو
    return render_template('projects/edit.html', project=project)

@project_bp.route('/<int:project_id>', methods=['PUT', 'POST'])
def update_project(project_id):
    """تحديث مشروع محدد"""
    project = Project.query.get_or_404(project_id)
    data = request.form
    
    # تحديث بيانات المشروع
    project.name = data.get('name', project.name)
    project.manager = data.get('manager', project.manager)
    project.location = data.get('location', project.location)
    project.spreadsheet_id = data.get('spreadsheet_id', project.spreadsheet_id)
    
    # حفظ التغييرات
    db.session.commit()
    
    # إذا كان الطلب من واجهة API
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(project.to_dict())
    
    # إعادة التوجيه إلى صفحة المشروع
    return redirect(url_for('project.get_project', project_id=project.id))

@project_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """حذف مشروع محدد"""
    project = Project.query.get_or_404(project_id)
    
    # حذف المشروع من قاعدة البيانات
    db.session.delete(project)
    db.session.commit()
    
    # إذا كان الطلب من واجهة API
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': 'تم حذف المشروع بنجاح'})
    
    # إعادة التوجيه إلى صفحة المشاريع
    return redirect(url_for('project.get_projects'))

@project_bp.route('/<int:project_id>/dashboard', methods=['GET'])
def project_dashboard(project_id):
    """عرض لوحة تحكم المشروع"""
    project = Project.query.get_or_404(project_id)
    # تم التعديل هنا: نمرر كائن المشروع الأصلي مباشرة
    return render_template('projects/dashboard.html', project=project)

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.project import Project
from app.models.item import Item
from app.extensions import db
from flask_login import login_required

project_bp = Blueprint("project", __name__)

@project_bp.route("/projects")
@login_required
def get_projects():
    projects = Project.query.all()
    return render_template("projects/index.html", projects=projects)

@project_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        status = request.form["status"]
        notes = request.form["notes"]
        spreadsheet_id = request.form.get("spreadsheet_id") # Optional

        new_project = Project(name=name, location=location, start_date=start_date, 
                              end_date=end_date, status=status, notes=notes,
                              spreadsheet_id=spreadsheet_id)
        db.session.add(new_project)
        db.session.commit()
        flash("تم إضافة المشروع بنجاح!", "success")
        return redirect(url_for("project.get_projects"))
    return render_template("projects/new.html")

@project_bp.route("/projects/<int:project_id>")
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("projects/show.html", project=project)

@project_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        project.name = request.form["name"]
        project.location = request.form["location"]
        project.start_date = request.form["start_date"]
        project.end_date = request.form["end_date"]
        project.status = request.form["status"]
        project.notes = request.form["notes"]
        project.spreadsheet_id = request.form.get("spreadsheet_id")
        db.session.commit()
        flash("تم تحديث المشروع بنجاح!", "success")
        return redirect(url_for("project.get_project", project_id=project.id))
    return render_template("projects/edit.html", project=project)

@project_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("تم حذف المشروع بنجاح!", "success")
    return redirect(url_for("project.get_projects"))

@project_bp.route("/projects/<int:project_id>/dashboard")
@login_required
def project_dashboard(project_id):
    project = Project.query.get_or_404(project_id)
    items = Item.query.filter_by(project_id=project.id).all()

    # Calculate data for charts
    contract_costs = [item.contract_total_cost for item in items]
    actual_costs = [item.actual_total_cost for item in items if item.actual_total_cost is not None]
    item_descriptions = [item.description for item in items]

    # Prepare data for JSON response
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
    projects = Project.query.all()
    
    total_contract_cost_all = sum(p.total_contract_cost for p in projects)
    total_actual_cost_all = sum(p.total_actual_cost for p in projects)
    total_savings_all = sum(p.total_savings for p in projects)
    total_paid_amount_all = sum(p.total_paid_amount for p in projects)
    total_remaining_amount_all = sum(p.total_remaining_amount for p in projects)

    # Data for charts (example: status distribution across all projects)
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


