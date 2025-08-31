from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.fields import DateField # استخدام حقل التاريخ الصحيح
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from wtforms_sqlalchemy.fields import QuerySelectField # لاستيراد حقل القائمة المنسدلة من قاعدة البيانات
from app.models.user import User

# ... (LoginForm و RegisterForm يبقيان كما هما) ...
class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول."""
    username = StringField('اسم المستخدم', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    submit = SubmitField('تسجيل الدخول')

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

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('اسم المستخدم هذا موجود بالفعل. الرجاء اختيار اسم آخر.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('البريد الإلكتروني هذا مسجل بالفعل. الرجاء استخدام بريد آخر.')

# --- START: إضافة نموذج المشروع ---

# دالة مساعدة لجلب قائمة المستخدمين لعرضها في القائمة المنسدلة
def get_users():
    return User.query.all()

class ProjectForm(FlaskForm):
    """نموذج لإضافة أو تعديل مشروع."""
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
    
    # حقل ديناميكي لجلب مدراء المشاريع من قاعدة البيانات
    manager = QuerySelectField(
        'مدير المشروع',
        query_factory=get_users,
        get_label='username',
        allow_blank=True,
        blank_text='-- اختر مديرًا للمشروع --',
        validators=[Optional()]
    )
    submit = SubmitField('حفظ المشروع')
# --- END: إضافة نموذج المشروع ---