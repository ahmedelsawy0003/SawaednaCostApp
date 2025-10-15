from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models.user import User
from app.models.contractor import Contractor
from app.models.invoice import Invoice
from app.models.item import Item
from app import constants

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم أو البريد الإلكتروني', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    submit = SubmitField('تسجيل الدخول')

class RegisterForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(message="اسم المستخدم مطلوب."), Length(min=4, max=25, message="يجب أن يكون اسم المستخدم بين 4 و 25 حرفاً.")])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(message="البريد الإلكتروني مطلوب."), Email(message="البريد الإلكتروني غير صالح.")])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message="كلمة المرور مطلوبة."), Length(min=6, message="يجب أن لا تقل كلمة المرور عن 6 أحرف.")])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(message="تأكيد كلمة المرور مطلوب."), EqualTo('password', message='كلمتا المرور غير متطابقتين.')])
    submit = SubmitField('تسجيل الحساب')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('اسم المستخدم مسجل بالفعل. الرجاء اختيار اسم آخر.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('البريد الإلكتروني مسجل بالفعل. الرجاء استخدام بريد آخر.')


class ProjectForm(FlaskForm):
    name = StringField('اسم المشروع', validators=[DataRequired(message="اسم المشروع مطلوب.")])
    location = StringField('الموقع (اختياري)')
    start_date = DateField('تاريخ البداية', validators=[Optional()])
    end_date = DateField('تاريخ النهاية', validators=[Optional()])
    status = SelectField('الحالة', choices=constants.PROJECT_STATUS_CHOICES, validators=[DataRequired()])
    notes = TextAreaField('ملاحظات')
    spreadsheet_id = StringField('معرّف Google Sheets')
    manager_id = SelectField('مدير المشروع', coerce=int, validators=[Optional()])
    submit = SubmitField('حفظ المشروع')

class ContractorForm(FlaskForm):
    name = StringField('اسم المقاول', validators=[DataRequired(message="اسم المقاول مطلوب.")])
    contact_person = StringField('اسم شخص الاتصال')
    phone = StringField('رقم الهاتف')
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(message="البريد الإلكتروني غير صالح.")])
    notes = TextAreaField('ملاحظات')
    submit = SubmitField('حفظ التعديلات')

    def __init__(self, original_name=None, *args, **kwargs):
        super(ContractorForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if self.original_name and self.original_name.lower() == name.data.lower():
            return
        if Contractor.query.filter(Contractor.name.ilike(name.data)).first():
            raise ValidationError('مقاول بهذا الاسم مسجل بالفعل. يجب أن يكون الاسم فريداً.')

# --- START: تحديث نموذج المستخلص ---
class InvoiceForm(FlaskForm):
    invoice_number = StringField('رقم المستخلص/الفاتورة', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    invoice_date = DateField('تاريخ المستخلص/الفاتورة', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    contractor_id = SelectField('المقاول / المورد', coerce=int, validators=[DataRequired(message="الرجاء اختيار مقاول أو مورد.")])
    invoice_type = SelectField('نوع المستخلص', choices=constants.INVOICE_TYPE_CHOICES, validators=[DataRequired()])
    purchase_order_number = StringField('رقم أمر الشراء (PO)')
    disbursement_order_number = StringField('رقم أمر الصرف/المصادقة')
    notes = TextAreaField('ملاحظات (اختياري)')
    submit = SubmitField('إنشاء المستخلص والانتقال لإضافة البنود')

    def __init__(self, project_id=None, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.project_id = project_id

    def validate_invoice_number(self, invoice_number):
        if self.project_id:
            existing_invoice = Invoice.query.filter_by(
                project_id=self.project_id, 
                invoice_number=invoice_number.data
            ).first()
            if existing_invoice:
                raise ValidationError('رقم المستخلص مسجل بالفعل في هذا المشروع. يرجى اختيار رقم آخر.')
# --- END: تحديث نموذج المستخلص ---

class ItemForm(FlaskForm):
    item_number = StringField('رقم البند', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    description = TextAreaField('الوصف', validators=[DataRequired(message="هذا الحقل مطلوب.")])
    unit = StringField('الوحدة')
    
    purchase_order_number = StringField('رقم أمر الشراء (اختياري)')
    disbursement_order_number = StringField('رقم أمر الصرف (اختياري)')

    contract_quantity = FloatField('الكمية التعاقدية', validators=[Optional()])
    contract_unit_cost = FloatField('التكلفة الإفرادية التعاقدية', validators=[Optional()])
    
    actual_quantity = FloatField('الكمية المتاحة للفوترة', validators=[Optional()])
    actual_unit_cost = FloatField('تكلفة الوحدة للمستخلص (يدوي)', validators=[Optional()])
    
    status = SelectField('الحالة', choices=constants.ITEM_STATUS_CHOICES, validators=[DataRequired()])
    contractor_id = SelectField('المقاول المسؤول عن البند', coerce=int, validators=[Optional()])
    notes = TextAreaField('ملاحظات')
    submit = SubmitField('حفظ التغييرات')

    def __init__(self, project_id=None, original_item_number=None, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.project_id = project_id
        self.original_item_number = original_item_number

    def validate_item_number(self, item_number):
        if self.original_item_number and self.original_item_number.lower() == item_number.data.lower():
            return
        existing_item = Item.query.filter_by(project_id=self.project_id, item_number=item_number.data).first()
        if existing_item:
            raise ValidationError('رقم البند مسجل بالفعل في هذا المشروع.')