import os

class Config:
    # يقرأ المفتاح السري من متغير البيئة الذي أنشأته في Vercel
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # يقرأ رابط قاعدة البيانات من متغير البيئة DATABASE_URL
    # Vercel يستخدم هذا الاسم افتراضياً لقواعد البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # هذا الإعداد يُفضل إبقاؤه لإيقاف رسائل غير ضرورية
    SQLALCHEMY_TRACK_MODIFICATIONS = False