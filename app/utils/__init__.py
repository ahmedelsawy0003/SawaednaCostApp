"""
Utility functions for the application
"""
from flask_login import current_user
from flask import abort
from functools import wraps
import re


def check_project_permission(project):
    """
    التحقق من صلاحية المستخدم للوصول للمشروع
    Check if current user has permission to access the project
    
    Args:
        project: Project object to check permission for
        
    Returns:
        bool: True if user has permission
        
    Raises:
        401: If user is not authenticated
        403: If user doesn't have permission
    """
    if not current_user.is_authenticated:
        abort(401)  # Unauthorized
    
    # يمكنك إضافة منطق الصلاحيات هنا
    # مثلاً: التحقق من أن المستخدم مالك المشروع أو عضو فيه
    # For now, allow all authenticated users
    # You can add more complex permission logic here:
    # - Check if user is project owner
    # - Check if user is project member
    # - Check user role/permissions
    
    return True


def sanitize_input(text):
    """
    تنظيف النصوص من HTML و JavaScript الضار
    Sanitize input text to prevent XSS attacks
    
    Args:
        text: Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return text
    
    # Convert to string
    text = str(text)
    
    # إزالة HTML tags
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # إزالة الأحرف الخاصة الخطرة
    # Remove dangerous special characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '`']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # إزالة JavaScript patterns
    # Remove JavaScript patterns
    js_patterns = [
        r'javascript:',
        r'on\w+\s*=',
        r'<script',
        r'</script>',
    ]
    for pattern in js_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()


def require_project_access(f):
    """
    Decorator للتحقق من صلاحية الوصول للمشروع
    Decorator to check project access permission
    
    Usage:
        @require_project_access
        def view_project(project_id):
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        project_id = kwargs.get('project_id')
        if project_id:
            from app.models.project import Project
            project = Project.query.get_or_404(project_id)
            check_project_permission(project)
        return f(*args, **kwargs)
    return decorated_function


def format_currency(amount, currency='EGP'):
    """
    تنسيق المبالغ المالية
    Format currency amounts
    
    Args:
        amount: Numeric amount
        currency: Currency code (default: EGP)
        
    Returns:
        str: Formatted currency string
    """
    try:
        amount = float(amount)
        return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return f"0.00 {currency}"


def calculate_percentage(part, total):
    """
    حساب النسبة المئوية
    Calculate percentage
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        float: Percentage (0-100)
    """
    try:
        if total == 0:
            return 0.0
        return (float(part) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def validate_file_extension(filename, allowed_extensions=None):
    """
    التحقق من امتداد الملف
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (default: xlsx, xls, pdf)
        
    Returns:
        bool: True if extension is allowed
    """
    if allowed_extensions is None:
        allowed_extensions = {'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg'}
    
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def truncate_text(text, length=50, suffix='...'):
    """
    اختصار النص
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if not text:
        return ''
    
    text = str(text)
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix


# Export all utility functions
__all__ = [
    'check_project_permission',
    'sanitize_input',
    'require_project_access',
    'format_currency',
    'calculate_percentage',
    'validate_file_extension',
    'truncate_text',
]

