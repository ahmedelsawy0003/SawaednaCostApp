# 1. المرحلة الأساسية: استخدام صورة Python 3.11 النظيفة
FROM python:3.11-slim

# 2. تعيين متغيرات البيئة الأساسية
ENV PORT 8080
ENV FLASK_APP index.py

# 3. تعيين دليل العمل في الحاوية
WORKDIR /usr/src/app

# 4. تثبيت متطلبات نظام التشغيل (تم حذف حزمة libgdk-pixbuf2.0-0 و libatlas-base-dev)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    build-essential \
    python3-dev \
    libcairo2 \
    libpango-1.0-0 \
    libffi-dev \
    gfortran \
    libopenblas-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. تثبيت مكتبات Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# --- أضف هذا السطر الجديد لفرض إصلاح التعارض الثنائي ---
RUN pip install --no-cache-dir --upgrade numpy pandas

# 6. نسخ باقي ملفات المشروع
COPY . .

# 7. تعريف أمر التشغيل باستخدام Gunicorn
CMD exec gunicorn --bind :$PORT --workers 4 --timeout 120 index:app