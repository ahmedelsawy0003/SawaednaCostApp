import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from app.models.project import Project
from app.models.item import Item
from app.services.google_sheets_service import GoogleSheetsService
from app.extensions import db

# تحميل متغيرات البيئة
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # تكوين التطبيق
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///project_costs.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # تسجيل النماذج
    from app.routes.project_routes import project_bp
    from app.routes.item_routes import item_bp
    from app.routes.google_sheets_routes import sheets_bp
    
    app.register_blueprint(project_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(sheets_bp)
    
    # إنشاء قاعدة البيانات
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False)