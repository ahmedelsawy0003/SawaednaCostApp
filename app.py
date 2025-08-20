from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Test Successful! The server is running.</h1>"

# ملاحظة: هذا مجرد اختبار مؤقت وسنعيد الكود الأصلي لاحقاً