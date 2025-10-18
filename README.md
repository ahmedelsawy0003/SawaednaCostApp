# 🏗️ سواعدنا - نظام إدارة المشاريع والتكاليف

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

نظام متكامل واحترافي لإدارة المشاريع الإنشائية والتكاليف، مع ميزات متقدمة لإدارة المواد والمدفوعات وجداول الكميات.

---

## ✨ الميزات الرئيسية

### 🎨 واجهة مستخدم احترافية
- **Light/Dark Mode**: تبديل سلس بين الوضع الفاتح والداكن
- **تصميم responsive**: يعمل بشكل مثالي على جميع الأجهزة
- **مستوحى من**: Hive.com و Wrike.com
- **RTL Support**: دعم كامل للغة العربية

### 📋 إدارة النماذج
- **طلبات توريد المواد**: عدة بنود لكل طلب مع تاريخ توريد لكل بند
- **مرتجعات المواد**: إدارة كاملة للمرتجعات مع ملاحظات تفصيلية
- **نظام موافقات**: مسودة → قيد المراجعة → معتمد/مرفوض → مكتمل
- **تصدير واستيراد Excel**: قوالب جاهزة ورفع ملفات
- **تصدير PDF**: للطباعة والأرشفة

### 💰 إدارة المدفوعات
- **أوامر الصرف**: للمقاولين، العمالة، المشتريات، وغيرها
- **أوامر الشراء**: نظام متكامل لإدارة المشتريات
- **سجل الدفعات**: تتبع شامل لجميع المدفوعات
- **ربط بالمشاريع والبنود**: تتبع دقيق للتكاليف

### 📊 جداول الكميات (BOQ)
- **إدارة البنود**: إضافة وتعديل بنود جدول الكميات
- **تتبع التنفيذ**: الكمية المنفذة ونسبة الإنجاز
- **حسابات تلقائية**: القيمة المنفذة والمتبقية
- **تصدير Excel**: لمشاركة البيانات

### 🔢 نظام ترقيم فريد
- **لا يتكرر أبداً**: ضمان عدم تكرار الأرقام
- **تنسيق موحد**: `PREFIX-YYYY-XXXX`
- **أنواع**:
  - `MR-2025-0001`: طلبات المواد
  - `RT-2025-0002`: مرتجعات المواد
  - `PO-2025-0003`: أوامر الشراء
  - `PY-2025-0004`: أوامر الصرف

---

## 🚀 البدء السريع

### المتطلبات
- Python 3.11+
- PostgreSQL (أو Neon Database)
- pip

### التثبيت

```bash
# 1. Clone المشروع
git clone https://github.com/ahmedelsawy0003/SawaednaCostApp.git
cd SawaednaCostApp

# 2. إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # على Windows: venv\Scripts\activate

# 3. تثبيت المكتبات
pip install -r requirements.txt

# 4. إعداد متغيرات البيئة
cp .env.example .env
# عدّل .env وأضف:
# DATABASE_URL=postgresql://user:password@localhost/dbname
# SECRET_KEY=your-secret-key-here

# 5. تشغيل Migration
flask db upgrade

# 6. تشغيل التطبيق
python index.py
```

التطبيق سيعمل على: `http://localhost:5000`

---

## 📂 هيكل المشروع

```
SawaednaCostApp/
├── app/
│   ├── models/          # قاعدة البيانات
│   ├── routes/          # المسارات والـ APIs
│   ├── utils/           # وظائف مساعدة
│   └── __init__.py      # تهيئة التطبيق
├── static/
│   ├── css/             # الأنماط
│   └── js/              # السكريبتات
├── templates/           # قوالب HTML
├── migrations/          # ملفات Migration
├── requirements.txt     # المكتبات
├── config.py            # الإعدادات
└── index.py             # نقطة الدخول
```

---

## 🗄️ قاعدة البيانات

### Models الرئيسية

| Model | الوصف |
|-------|-------|
| `User` | المستخدمون |
| `Project` | المشاريع |
| `MaterialRequest` | طلبات المواد |
| `MaterialReturn` | مرتجعات المواد |
| `PaymentOrder` | أوامر الصرف |
| `BOQItem` | بنود جدول الكميات |
| `SequenceCounter` | نظام الترقيم |

### العلاقات
- كل طلب/مرتجع مرتبط بمشروع (إجباري)
- كل طلب/مرتجع يمكن ربطه ببند (اختياري)
- كل طلب/مرتجع له عدة بنود (One-to-Many)
- نظام موافقات متكامل مع المستخدمين

---

## 📖 دليل الاستخدام

### إنشاء طلب مواد

**الطريقة 1: يدوياً**
1. اذهب إلى **النماذج** → **طلبات توريد المواد**
2. اضغط **طلب جديد**
3. املأ البيانات:
   - اختر المشروع (إجباري)
   - أضف البنود (اسم المادة، الكمية، تاريخ التوريد)
4. احفظ كمسودة أو أرسل للمراجعة

**الطريقة 2: رفع Excel**
1. حمّل القالب الفارغ
2. املأ البيانات في Excel
3. ارفع الملف
4. راجع وأكّد

### تصدير البيانات

**Excel:**
- مثالي للتعديل والمشاركة
- يحتوي على جميع التفاصيل
- يمكن إعادة استيراده

**PDF:**
- مثالي للطباعة
- للأرشفة والتوقيعات
- تنسيق احترافي

---

## 🎨 Light/Dark Mode

### التبديل
- **زر التبديل**: في شريط التنقل العلوي
- **اختصار لوحة المفاتيح**: `Ctrl+Shift+T`
- **تلقائي**: يكتشف تفضيلات النظام

### الحفظ
- يحفظ اختيارك تلقائياً في `localStorage`
- يبقى الاختيار عند إعادة فتح التطبيق

---

## 🔐 الأمان

- ✅ **CSRF Protection**: حماية من هجمات CSRF
- ✅ **Login Required**: جميع الصفحات محمية
- ✅ **Input Validation**: التحقق من المدخلات
- ✅ **SQL Injection Protection**: SQLAlchemy ORM
- ✅ **Password Hashing**: تشفير كلمات المرور

---

## 🚢 النشر على Vercel

### الخطوات

1. **إنشاء حساب على Neon Database**
   ```
   https://neon.tech
   ```

2. **إنشاء قاعدة بيانات**
   - احصل على `DATABASE_URL`

3. **إعداد Vercel**
   ```bash
   # تثبيت Vercel CLI
   npm i -g vercel
   
   # تسجيل الدخول
   vercel login
   
   # النشر
   vercel
   ```

4. **إضافة متغيرات البيئة في Vercel**
   - `DATABASE_URL`
   - `SECRET_KEY`

5. **تشغيل Migration**
   ```bash
   # محلياً مع DATABASE_URL من Neon
   flask db upgrade
   ```

---

## 📊 الإحصائيات

- **عدد الملفات**: 50+ ملف
- **عدد Models**: 15+ model
- **عدد Routes**: 100+ route
- **عدد Templates**: 30+ template
- **سطور الكود**: 10,000+ سطر

---

## 🛠️ التقنيات المستخدمة

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM
- **Flask-Login**: Authentication
- **Flask-Migrate**: Database migrations

### Frontend
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icons
- **Cairo Font**: Arabic typography
- **Custom CSS**: Light/Dark themes

### Excel & PDF
- **openpyxl**: Excel read/write
- **pandas**: Data processing
- **reportlab**: PDF generation
- **weasyprint**: Advanced PDF

### Database
- **PostgreSQL**: Production database
- **Neon**: Serverless PostgreSQL

---

## 📝 التوثيق الكامل

للتوثيق الشامل، راجع:
- `FINAL_PROJECT_DOCUMENTATION.md`: التوثيق التقني الكامل
- `IMPLEMENTATION_SUMMARY.md`: ملخص التطوير

---

## 🤝 المساهمة

نرحب بالمساهمات! الرجاء:
1. Fork المشروع
2. إنشاء Branch جديد (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى Branch (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

---

## 📄 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE)

---

## 👨‍💻 المطور

**Ahmed Elsawy**
- GitHub: [@ahmedelsawy0003](https://github.com/ahmedelsawy0003)
- Email: [أضف بريدك]

---

## 🙏 شكر وتقدير

- **Hive.com**: للإلهام في تصميم Dark Mode
- **Wrike.com**: للإلهام في تصميم Light Mode
- **Bootstrap**: للـ UI framework
- **Font Awesome**: للأيقونات
- **Flask Community**: للدعم والمساعدة

---

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل:
- **Issues**: [GitHub Issues](https://github.com/ahmedelsawy0003/SawaednaCostApp/issues)
- **Email**: [أضف بريدك]

---

## 🗺️ خارطة الطريق

### الإصدار 2.1 (قريباً)
- [ ] تطبيق موبايل (PWA)
- [ ] نظام إشعارات
- [ ] تقارير متقدمة
- [ ] تكامل مع WhatsApp

### الإصدار 3.0 (مستقبلاً)
- [ ] AI للتنبؤ بالتكاليف
- [ ] Dashboard تفاعلي
- [ ] API عام
- [ ] Multi-tenancy

---

**صُنع بـ ❤️ في مصر**


