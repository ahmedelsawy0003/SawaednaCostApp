from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# START: New Association Table for User-Project relationship
# This table links users to projects and defines their role on that project
user_project_association = db.Table(
    'user_project',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('role', db.String(50), default='viewer')  # e.g., 'viewer', 'editor'
)
# END: New Association Table

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default='user')  # 'user' or 'admin'

    # START: New relationship to projects
    projects = db.relationship(
        'Project', 
        secondary=user_project_association,
        back_populates='users'
    )
    # END: New relationship

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'