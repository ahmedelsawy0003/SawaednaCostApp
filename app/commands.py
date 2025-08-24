import click
from flask.cli import with_appcontext
from .models.user import User
from .extensions import db

@click.command(name='create-admin')
@with_appcontext
@click.argument('username')
def create_admin(username):
    """
    Sets a user's role to 'admin'.
    Usage: flask create-admin <your_username>
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f"User '{username}' not found.")
        return

    user.role = 'admin'
    db.session.commit()
    click.echo(f"User '{username}' has been promoted to Admin.")

def init_app(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(create_admin)