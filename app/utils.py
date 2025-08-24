from flask import abort
from flask_login import current_user

def check_project_permission(project):
    """
    Checks if the current user has permission to access a project.
    An admin has access to all projects.
    A regular user only has access to their associated projects.
    If no permission, it aborts with a 403 Forbidden error.
    """
    if current_user.role != 'admin' and project not in current_user.projects:
        abort(403)