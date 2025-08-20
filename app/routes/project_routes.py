from flask import Blueprint

project_bp = Blueprint('project', __name__, url_prefix='/projects')

@project_bp.route('/')
def get_projects():
    return "<h1>صفحة المشاريع تعمل - Test OK</h1>"

@project_bp.route('/new')
def new_project():
    return "<h1>صفحة مشروع جديد تعمل - Test OK</h1>"

# ملاحظة: هذا مجرد كود اختبار مؤقت