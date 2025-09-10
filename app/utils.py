from flask import abort
from flask_login import current_user
import bleach

def check_project_permission(project, require_admin=False):
    """
    Checks if the current user has permission to access a project.
    Admins/Sub-admins have access to all projects.
    Regular users only have access to their associated projects.
    The 'require_admin' flag can restrict access to admins/sub-admins only.
    """
    # If the action requires an admin role, check that first.
    if require_admin and current_user.role not in ['admin', 'sub-admin']:
        abort(403)

    # For general access, check if the user is an admin or has the project assigned.
    if current_user.role not in ['admin', 'sub-admin']:
        try:
            allowed_project_ids = {p.id for p in current_user.projects}
        except Exception:
            allowed_project_ids = set()
        if project.id not in allowed_project_ids:
            abort(403)

# START: Corrected Sanitization Function
def sanitize_input(data):
    """
    Cleans user-submitted data to prevent XSS attacks.
    It removes any HTML tags, leaving only plain text.
    """
    if data:
        # The 'styles' argument has been removed to fix the TypeError
        return bleach.clean(data, tags=[], attributes={}, strip=True)
    return data
# END: Corrected Sanitization Function