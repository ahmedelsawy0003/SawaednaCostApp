import os
from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import datetime

# استيراد النماذج والإضافات
from app.models.project import Project
from app.extensions import db

# تحميل متغيرات البيئة
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # تكوين التطبيق
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # تسجيل المسارات (Blueprints)
    from app.routes.project_routes import project_bp
    from app.routes.item_routes import item_bp
    from app.routes.google_sheets_routes import sheets_bp
    
    app.register_blueprint(project_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(sheets_bp)
    
    # إنشاء جداول قاعدة البيانات إذا لم تكن موجودة
    with app.app_context():
        db.create_all()
    
    # تعديل المسار الرئيسي لعرض قائمة المشاريع
    @app.route('/')
    def index():
        """
        الصفحة الرئيسية التي تعرض كل المشاريع.
        """
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return render_template('projects/index.html', projects=[p.to_dict() for p in projects])
    
    # معالج السياق لتوفير التاريخ الحالي لكل القوالب
    @app.context_processor
    def inject_now():
        """
        يوفر متغير 'now' الذي يحتوي على التاريخ والوقت الحالي لكل قوالب Jinja2.
        """
        return {'now': datetime.utcnow()}
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False)