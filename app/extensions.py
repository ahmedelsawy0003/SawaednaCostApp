from flask_sqlalchemy import SQLAlchemy

# إنشاء كائن قاعدة البيانات
db = SQLAlchemy()

from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

