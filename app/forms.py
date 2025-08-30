from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User # نحتاج لاستيراد نموذج المستخدم للتحقق من وجوده

class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول."""
    username = StringField('اسم المستخدم', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    submit = SubmitField('تسجيل الدخول')

# --- START: إضافة نموذج التسجيل الجديد ---
class RegisterForm(FlaskForm):
    """نموذج تسجيل مستخدم جديد."""
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message="اسم المستخدم مطلوب."),
        Length(min=4, max=25, message="يجب أن يكون اسم المستخدم بين 4 و 25 حرفاً.")
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message="البريد الإلكتروني مطلوب."),
        Email(message="البريد الإلكتروني غير صالح.")
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message="كلمة المرور مطلوبة."),
        Length(min=6, message="يجب أن تكون كلمة المرور 6 أحرف على الأقل.")
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message="تأكيد كلمة المرور مطلوب."),
        EqualTo('password', message='كلمتا المرور غير متطابقتين.')
    ])
    submit = SubmitField('تسجيل الحساب')

    # دوال التحقق المخصصة
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('اسم المستخدم هذا موجود بالفعل. الرجاء اختيار اسم آخر.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('البريد الإلكتروني هذا مسجل بالفعل. الرجاء استخدام بريد آخر.')
# --- END: إضافة نموذج التسجيل الجديد ---