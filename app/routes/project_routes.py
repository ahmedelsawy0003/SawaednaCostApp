from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models.project import Project
from app.extensions import db

project_bp = Blueprint('project', __name__, url_prefix='/projects')

@project_bp.route('/', methods=['GET'])
def get_projects():
    """الحصول على قائمة المشاريع"""
    projects = Project.query.all()
    return render_template('projects/index.html', projects=[project.to_dict() for project in projects])

@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """الحصول على مشروع محدد"""
    project = Project.query.get_or_404(project_id)
    return render_template('projects/show.html', project=project.to_dict())

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
    return render_template('projects/edit.html', project=project.to_dict())

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
    return render_template('projects/dashboard.html', project=project.to_dict())