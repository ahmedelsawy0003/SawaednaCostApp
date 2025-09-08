from flask import Flask, redirect, url_for
from flask_login import current_user
from .extensions import db, migrate, login_manager
from . import commands

# Import models to ensure they are registered with SQLAlchemy
from .models.user import User
from .models.project import Project
from .models.item import Item
from .models.payment import Payment
from .models.audit_log import AuditLog
from .models.contractor import Contractor
from .models.invoice import Invoice
from .models.invoice_item import InvoiceItem
from .models.cost_detail import CostDetail
from .models.payment_distribution import PaymentDistribution

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db) 
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    commands.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_sidebar_data():
        sidebar_projects = []
        sidebar_contractors = []
        if current_user.is_authenticated:
            if current_user.role in ['admin', 'sub-admin']:
                sidebar_projects = Project.query.filter_by(is_archived=False).order_by(Project.name).all()
                sidebar_contractors = Contractor.query.order_by(Contractor.name).all()
            else:
                sidebar_projects = Project.query.join(User.projects).filter(User.id == current_user.id, Project.is_archived==False).order_by(Project.name).all()
                if sidebar_projects:
                    project_ids = [p.id for p in sidebar_projects]
                    sidebar_contractors = Contractor.query.join(Invoice).filter(Invoice.project_id.in_(project_ids)).distinct().order_by(Contractor.name).all()
        return dict(
            sidebar_projects=sidebar_projects,
            sidebar_contractors=sidebar_contractors
        )

    # Import and register blueprints
    from .routes.project_routes import project_bp
    from .routes.item_routes import item_bp
    from .routes.google_sheets_routes import sheets_bp
    from .routes.auth_routes import auth_bp
    from .routes.contractor_routes import contractor_bp
    from .routes.invoice_routes import invoice_bp
    from .routes.cost_detail_routes import cost_detail_bp
    from .routes.payment_routes import payment_bp  # <-- سطر الاستيراد المضاف

    app.register_blueprint(project_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(sheets_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(contractor_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(cost_detail_bp)
    app.register_blueprint(payment_bp)  # <-- سطر التسجيل المضاف
    
    @app.route('/')
    def index():
        return redirect(url_for('project.get_projects'))
   
    return app