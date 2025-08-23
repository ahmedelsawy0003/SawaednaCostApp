from flask import Flask
from app.extensions import db, migrate, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.project_routes import project_bp
    from app.routes.item_routes import item_bp
    from app.routes.google_sheets_routes import sheets_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.payment_routes import payment_bp

    app.register_blueprint(project_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(sheets_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)

    with app.app_context():
        db.create_all()

    return app

