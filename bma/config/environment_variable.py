from pathlib import Path
import environ
import os
from datetime import timedelta

env = environ.Env(
    DEBUG=(bool, False),
)

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Core
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
MEDIA_URL = env("MEDIA_URL")

# Database
DB_NAME = env("DB_NAME")
DB_USER = env("DB_USER")
DB_PASS = env("DB_PASS")
DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT")

# CORS
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)

# Celery
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = env.list("CELERY_ACCEPT_CONTENT", default=["json"])
CELERY_TASK_SERIALIZER = env("CELERY_TASK_SERIALIZER", default="json")
CELERY_TIMEZONE = env("CELERY_TIMEZONE", default="UTC")
CELERY_TASK_TRACK_STARTED = env.bool("CELERY_TASK_TRACK_STARTED", default=True)
CELERY_TASK_TIME_LIMIT = env.int("CELERY_TASK_TIME_LIMIT", default=1800)

# Redis
REDIS_URL = env("REDIS_URL")

# Email
EMAIL_HOST = env("EMAIL_HOST", default=None)
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default=None)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="Dev App <no-reply@localhost>",
)

# JWT (SimpleJWT expects timedelta)
ACCESS_TOKEN_LIFETIME = timedelta(
    minutes=env.int("ACCESS_TOKEN_LIFETIME", default=5)
)

REFRESH_TOKEN_LIFETIME = timedelta(
    days=env.int("REFRESH_TOKEN_LIFETIME", default=1)
)


#Google
GOOGLE_CLIENT_ID=env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=env("GOOGLE_CLIENT_SECRET")

#Stripe
STRIPE_SECRET_KEY=env("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY=env("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET=env("STRIPE_WEBHOOK_SECRET")