<<<<<<< HEAD
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime

# استيراد الإضافات والنماذج
from app.extensions import db
from app.models.project import Project
from app.models.item import Item
from app.models.cost_detail import CostDetail

# تحميل متغيرات البيئة
load_dotenv()

def create_app():
    app = Flask(__name__)

    # --- كل الإعدادات يجب أن تكون هنا بالداخل ---

    # 1. تكوين التطبيق
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. تهيئة قاعدة البيانات مع التطبيق
    db.init_app(app)

    # 3. استيراد وتسجيل المسارات (Blueprints)
    from app.routes.project_routes import project_bp
    from app.routes.item_routes import item_bp
    from app.routes.google_sheets_routes import sheets_bp
    from app.routes.cost_detail_routes import cost_detail_bp # <-- السطر الجديد الأول

    app.register_blueprint(project_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(sheets_bp)
    app.register_blueprint(cost_detail_bp) # <-- السطر الجديد الثاني

    # 4. إضافة المسار الرئيسي ومعالج السياق
    @app.route('/')
    def index():
        """الصفحة الرئيسية التي تعرض كل المشاريع."""
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return render_template('projects/index.html', projects=projects)

    @app.context_processor
    def inject_now():
        """يوفر متغير 'now' لكل القوالب."""
        return {'now': datetime.utcnow()}

    # --- نهاية منطقة الإعدادات ---

    return app

# إنشاء التطبيق باستخدام الدالة
app = create_app()

# إنشاء الجداول ضمن سياق التطبيق لضمان عملها الصحيح
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
=======
from app import create_app
from flask import redirect, url_for

app = create_app()

@app.route('/')
def index():
    return redirect(url_for('project.get_projects'))

if __name__ == '__main__':
    app.run(debug=True)

>>>>>>> 7a3713e (Initial commit with updated files)
