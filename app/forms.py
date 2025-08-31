from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models.user import User

# ... LoginForm and RegisterForm remain the same ...
class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    submit = SubmitField('تسجيل الدخول')

class RegisterForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(message="اسم المستخدم مطلوب."), Length(min=4, max=25, message="يجب أن يكون اسم المستخدم بين 4 و 25 حرفاً.")])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(message="البريد الإلكتروني مطلوب."), Email(message="البريد الإلكتروني غير صالح.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="كلمة المرور مطلوبة."), Length(min=6, message="يجب أن تكون كلمة المرور 6 أحرف على الأقل.")])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(message="تأكيد كلمة المرور مطلوب."), EqualTo('password', message='كلمتا المرور غير متطابقتين.')])
    submit = SubmitField('تسجيل الحساب')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('اسم المستخدم هذا موجود بالفعل. الرجاء اختيار اسم آخر.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('البريد الإلكتروني هذا مسجل بالفعل. الرجاء استخدام بريد آخر.')


# --- START: تعديل نموذج المشروع ---
class ProjectForm(FlaskForm):
    name = StringField('اسم المشروع', validators=[DataRequired(message="اسم المشروع مطلوب.")])
    location = StringField('الموقع')
    start_date = DateField('تاريخ البداية', validators=[Optional()])
    end_date = DateField('تاريخ النهاية', validators=[Optional()])
    status = SelectField('الحالة', choices=[
        ('قيد التنفيذ', 'قيد التنفيذ'),
        ('مكتمل', 'مكتمل'),
        ('معلق', 'معلق'),
        ('ملغي', 'ملغي')
    ], validators=[DataRequired()])
    notes = TextAreaField('ملاحظات')
    spreadsheet_id = StringField('معرّف Google Sheets')
    
    # تم تغيير اسم الحقل وتحديد coerce=int لضمان أن القيمة رقمية
    manager_id = SelectField('مدير المشروع', coerce=int, validators=[Optional()])
    
    submit = SubmitField('حفظ المشروع')
# --- END: تعديل نموذج المشروع ---