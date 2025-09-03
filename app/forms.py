from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models.user import User
from app.models.contractor import Contractor

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
    manager_id = SelectField('مدير المشروع', coerce=int, validators=[Optional()])
    submit = SubmitField('حفظ المشروع')

# --- START: تحديث نموذج المقاول ---
class ContractorForm(FlaskForm):
    name = StringField('اسم المقاول', validators=[DataRequired(message="اسم المقاول مطلوب.")])
    contact_person = StringField('شخص الاتصال (اختياري)')
    phone = StringField('رقم الهاتف (اختياري)')
    email = StringField('البريد الإلكتروني (اختياري)', validators=[Optional(), Email(message="البريد الإلكتروني غير صالح.")])
    notes = TextAreaField('ملاحظات (اختياري)')
    submit = SubmitField('حفظ التعديلات') # <-- تغيير نص الزر

    def __init__(self, original_name=None, *args, **kwargs):
        super(ContractorForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        # إذا كان الاسم لم يتغير، فلا داعي للتحقق
        if self.original_name and self.original_name.lower() == name.data.lower():
            return
        # إذا تغير الاسم، تحقق من أنه غير مستخدم من قبل مقاول آخر
        if Contractor.query.filter(Contractor.name.ilike(name.data)).first():
            raise ValidationError('مقاول بنفس هذا الاسم موجود بالفعل.')
# --- END: تحديث نموذج المقاول ---