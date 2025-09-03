from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models.user import User
from app.models.contractor import Contractor
from app.models.invoice import Invoice
from app.models.item import Item # <-- إضافة جديدة

# ... (Previous forms remain the same) ...
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

class ContractorForm(FlaskForm):
    name = StringField('اسم المقاول', validators=[DataRequired(message="اسم المقاول مطلوب.")])
    contact_person = StringField('شخص الاتصال (اختياري)')
    phone = StringField('رقم الهاتف (اختياري)')
    email = StringField('البريد الإلكتروني (اختياري)', validators=[Optional(), Email(message="البريد الإلكتروني غير صالح.")])
    notes = TextAreaField('ملاحظات (اختياري)')
    submit = SubmitField('حفظ التعديلات')

    def __init__(self, original_name=None, *args, **kwargs):
        super(ContractorForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if self.original_name and self.original_name.lower() == name.data.lower():
            return
        if Contractor.query.filter(Contractor.name.ilike(name.data)).first():
            raise ValidationError('مقاول بنفس هذا الاسم موجود بالفعل.')

class InvoiceForm(FlaskForm):
    invoice_number = StringField('رقم المستخلص/الفاتورة', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    invoice_date = DateField('تاريخ المستخلص', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    contractor_id = SelectField('المقاول', coerce=int, validators=[DataRequired(message="يجب اختيار مقاول.")])
    notes = TextAreaField('ملاحظات (اختياري)')
    submit = SubmitField('إنشاء المستخلص والانتقال لإضافة البنود')

    def validate_invoice_number(self, invoice_number):
        if Invoice.query.filter_by(invoice_number=invoice_number.data).first():
            raise ValidationError('رقم المستخلص هذا موجود بالفعل. الرجاء إدخال رقم فريد.')

# --- START: تحديث نموذج البنود ---
class ItemForm(FlaskForm):
    item_number = StringField('رقم البند', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    description = TextAreaField('الوصف', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    unit = StringField('الوحدة')
    
    contract_quantity = FloatField('الكمية التعاقدية', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    contract_unit_cost = FloatField('التكلفة الإفرادية التعاقدية', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    
    actual_quantity = FloatField('الكمية الفعلية (اختياري)', validators=[Optional()])
    actual_unit_cost = FloatField('التكلفة الإفرادية الفعلية (اختياري)', validators=[Optional()])
    
    status = SelectField('الحالة', choices=[('نشط', 'نشط'), ('مكتمل', 'مكتمل'), ('معلق', 'معلق')], validators=[DataRequired()])
    contractor_id = SelectField('المقاول الرئيسي للبند (اختياري)', coerce=int, validators=[Optional()])
    notes = TextAreaField('ملاحظات (اختياري)')
    submit = SubmitField('إضافة البند')

    def __init__(self, project_id=None, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.project_id = project_id

    def validate_item_number(self, item_number):
        # التحقق من أن رقم البند فريد داخل المشروع المحدد فقط
        existing_item = Item.query.filter_by(project_id=self.project_id, item_number=item_number.data).first()
        if existing_item:
            raise ValidationError('هذا الرقم مستخدم بالفعل في هذا المشروع.')
# --- END: تحديث نموذج البنود ---