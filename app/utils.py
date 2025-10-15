from flask import abort
from flask_login import current_user
import bleach

def check_project_permission(project, require_admin=False):
    """
    Checks if the current user has permission to access a project. 
    If permission is denied, aborts the request with a 403 Forbidden status.

    Admins/Sub-admins: Have access to all projects.
    Regular users: Only have access to their associated projects.
    The 'require_admin' flag can restrict access to admins/sub-admins only.
    """
    # If the action requires an admin role, check that first.
    if require_admin and current_user.role not in ['admin', 'sub-admin']:
        # Access denied: Requires Admin/Sub-Admin role.
        abort(403)

    # For general access, check if the user is an admin or has the project assigned.
    if current_user.role not in ['admin', 'sub-admin']:
        try:
            allowed_project_ids = {p.id for p in current_user.projects}
        except Exception:
            allowed_project_ids = set()
        if project.id not in allowed_project_ids:
            # Access denied: Regular user without project assignment.
            abort(403)

# START: Corrected Sanitization Function
def sanitize_input(data):
    """
    Cleans user-submitted data to prevent XSS attacks and ensures only safe plain text remains.
    
    It يزيل أي وسوم HTML، تاركاً النص العادي فقط.
    """
    if data:
        # The 'styles' argument has been removed to fix the TypeError
        # Explicitly casting to str is safer in case non-string data is passed accidentally.
        return bleach.clean(str(data), tags=[], attributes={}, strip=True)
    return data
# END: Corrected Sanitization Function