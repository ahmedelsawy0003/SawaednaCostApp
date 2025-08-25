from flask import abort
from flask_login import current_user
import bleach

def check_project_permission(project):
    """
    Checks if the current user has permission to access a project.
    An admin has access to all projects.
    A regular user only has access to their associated projects.
    If no permission, it aborts with a 403 Forbidden error.
    """
    if current_user.role != 'admin' and project not in current_user.projects:
        abort(403)

# START: New Sanitization Function
def sanitize_input(data):
    """
    Cleans user-submitted data to prevent XSS attacks.
    It removes any HTML tags, leaving only plain text.
    """
    if data:
        return bleach.clean(data, tags=[], attributes={}, styles=[], strip=True)
    return data
# END: New Sanitization Function