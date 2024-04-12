from .base import *
from toukiApp.company_data import CompanyData

DEBUG = False

SECRET_KEY=env("DEV_SECRET_KEY")

ALLOWED_HOSTS = [
    "django-render-6agw.onrender.com",
    'aozoratouki.com', 
    'www.aozoratouki.com'
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# # DEFAULT_FROM_EMAIL = 't.saga@yahoo.ne.jp'    #送信元のアドレスを指定
# EMAIL_HOST = 'smtp.mail.yahoo.co.jp' 
# EMAIL_PORT = 465                            
# EMAIL_HOST_USER = 't.saga@yahoo.ne.jp'   
# EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
# EMAIL_USE_SSL = True   

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = CompanyData.MAIL_ADDRESS    #送信元のアドレスを指定
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = CompanyData.MAIL_ADDRESS
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True  

DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.postgresql',
        'NAME':'souzokutoukikun',
        'USER':'souzokutoukikun',
        'PASSWORD':'FYamYIRWv3826xBsE1w9NIY0yXQ9kuwF',
        'HOST':'dpg-cndci6f79t8c738dmkl0-a',
        # 'HOST':'dpg-cndci6f79t8c738dmkl0-a.singapore-postgres.render.com',
        'PORT':'5432',
    }
}

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 以下、GCP用に生成したものの
# データベース情報
# instance_name: toukiai
# project: toukiai-development
# database-version: POSTGRES_15
# tier: db-f1-micro
# region: asia-northeast1
# name: toukiai-development
# https://sqladmin.googleapis.com/sql/v1beta4/projects/toukiai-development/instances/toukiai
# users: toukiai-development_tatsuyasaga
# password: saga2497

# Cloud Storageバケット情報
# region:asia-northeast1
# gs://toukiai-development_souzokutoukikun

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': './logfile.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
}