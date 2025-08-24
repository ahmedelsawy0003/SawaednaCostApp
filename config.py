import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # <<< ابدأ الإضافة هنا
    # هذه الإعدادات ضرورية لجعل اتصال قاعدة البيانات مستقراً على Vercel
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
    # <<< انتهت الإضافة هنا