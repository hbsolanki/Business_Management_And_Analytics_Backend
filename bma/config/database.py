from bma.config import environment_variable

# Database settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environment_variable.DB_NAME,
        "USER":environment_variable.DB_USER,
        "PASSWORD":environment_variable.DB_PASS,
        "HOST": environment_variable.DB_HOST,
        "PORT":environment_variable.DB_PORT,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION":environment_variable.REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "capacity": 1000,
            "expiry": 10,
        },
    },
}

