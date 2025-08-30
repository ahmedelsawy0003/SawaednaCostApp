from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول."""
    username = StringField('اسم المستخدم', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    submit = SubmitField('تسجيل الدخول')