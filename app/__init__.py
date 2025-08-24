from flask import Flask
from .extensions import db, migrate, login_manager

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models.user import User
    from .models.project import Project
    from .models.item import Item
    from .models.payment import Payment
    from .models.cost_detail import CostDetail


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.project_routes import project_bp
    from .routes.item_routes import item_bp
    from .routes.google_sheets_routes import sheets_bp
    from .routes.auth_routes import auth_bp
    from .routes.payment_routes import payment_bp
    from .routes.cost_detail_routes import cost_detail_bp

    app.register_blueprint(project_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(sheets_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(cost_detail_bp)

    return app