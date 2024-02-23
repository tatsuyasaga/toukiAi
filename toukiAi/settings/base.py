"""
Django settings for toukiAi project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import environ
from decouple import config
from dj_database_url import parse as dburl

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env_file = BASE_DIR / ".env"
env.read_env(env_file)
# DJANGO_SETTINGS_MODULE = env("DJANGO_SETTINGS_MODULE")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# Application definition
INSTALLED_APPS = [
    "accounts.apps.AccountsConfig",
    "toukiApp.apps.ToukiappConfig",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',    
    'allauth',     
    'allauth.account',     
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.line',
    'allauth.socialaccount.providers.yahoo',
    # 'axes'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'toukiAi.urls'

TEMPLATE_DIR = BASE_DIR / "toukiAi/templates"
STATIC_DIR = BASE_DIR / "toukiAi/static"
MEDIA_DIR = BASE_DIR / "toukiAi/media"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'toukiAi.context_processors.media',
            ],
        },
    },
]

STATICFILES_DIRS = [STATIC_DIR]

WSGI_APPLICATION = 'toukiAi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# default_dburl = "sqlite:///" + str(BASE_DIR / "db.sqlite3")

# DATABASES = {
#     "default": config("DATABASE_URL", default=default_dburl, cast=dburl),
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS':{"min_length":8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ja-JP'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"

CSRF_FAILURE_VIEW='toukiApp.views.csrf_failure'

SUPERUSER_NAME = env("SUPERUSER_NAME")
SUPERUSER_EMAIL = env("SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = env("SUPERUSER_PASSWORD")

# 以下の設定を追加
SITE_ID = 1
 
AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',  # 一般ユーザー用(メールアドレス認証)
    'django.contrib.auth.backends.ModelBackend',  # 管理サイト用(ユーザー名認証)
)
 
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # メールアドレス認証に変更する設定
ACCOUNT_USERNAME_REQUIRED = False  # サインナップ、ログイン時のユーザーネーム認証をキャンセル
 
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # サインアップにメールアドレス確認を使用
ACCOUNT_EMAIL_REQUIRED = True

LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URL = 'toukiApp:step_one'  # ログイン成功後の遷移先の指定
SOCIALACCOUNT_LOGIN_REDIRECT_URL = 'toukiApp:step_one'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'toukiApp:step_one'
ACCOUNT_LOGOUT_REDIRECT_URL = 'toukiApp:index'  # ログアウト成功後の遷移先の指定
 
ACCOUNT_LOGOUT_ON_GET = True  # 確認を行わずログアウトする設定

ACCOUNT_FORMS = {
    "signup": "accounts.forms.CustomSignupForm",
    'login': 'accounts.forms.CustomLoginForm',
    "reset_password": "accounts.forms.CustomResetPasswordForm",
    "reset_password_from_key": "accounts.forms.CustomResetPasswordKeyForm",
    "reset_password_from_key_done": "accounts.forms.CustomResetPasswordKeyDoneForm",
    'change_password': 'accounts.forms.CustomChangePasswordForm',
}

SESSION_COOKIE_AGE = 604800

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 0
# ACCOUNT_ADAPTER = 'accounts.adapter.AccountAdapter'

# # ログインの試行回数制限
# LOGIN_ATTENPTS_LIMIT = 3
# LOGIN_ATTEMPTS_TIMEOUT = 60*5

# #axesの設定
# AXES_FAILURE_LIMIT = LOGIN_ATTENPTS_LIMIT
# AXES_LOCKOUT_TEMPLATE = "toukiapp/signin.html"
# AXES_COOKIE_NAME = "axes-cookies"
# AXES_LOCKOUT_URL = "/toukiapp/signin"

# HANDLER_403 = 'accounts.views.error_403'