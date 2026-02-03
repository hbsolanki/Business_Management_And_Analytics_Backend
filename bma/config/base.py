from pathlib import Path
import environ
import os
from bma.config import environment_variable

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =environment_variable.SECRET_KEY
DEBUG =environment_variable.DEBUG
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS=environment_variable.CORS_ALLOW_ALL_ORIGINS

# Application definition
django_apps=[
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'django_celery_beat',
    'drf_spectacular',
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    'channels'
]
project_app=[
    'apps.user',
    'apps.business_app',
    'apps.product',
    'apps.inventory',
    'apps.customer',
    'apps.invoice',
    'apps.analytics',
    'apps.cost_category',
    'apps.cost_month',
    'apps.chat',
    'apps.task',
    'apps.notification',
]
INSTALLED_APPS = django_apps + project_app

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "bma.urls"

WSGI_APPLICATION = "bma.wsgi.application"
ASGI_APPLICATION = "bma.asgi.application"

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

APPEND_SLASH = False

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

AUTH_USER_MODEL = "user.User"


MEDIA_URL = environment_variable.MEDIA_URL
MEDIA_ROOT = BASE_DIR / "media"

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

#Google
GOOGLE_CLIENT_ID=environment_variable.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=environment_variable.GOOGLE_CLIENT_SECRET

#STRIPE
STRIPE_SECRET_KEY=environment_variable.STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=environment_variable.STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=environment_variable.STRIPE_WEBHOOK_SECRET

#EMAIL
DEFAULT_FROM_EMAIL=environment_variable.DEFAULT_FROM_EMAIL
DEFAULT_FROM_NAME_EMAIL=environment_variable.DEFAULT_FROM_NAME_EMAIL
BREVO_API_KEY=environment_variable.BREVO_API_KEY
