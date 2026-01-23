from bma.config import environment_variable
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": environment_variable.ACCESS_TOKEN_LIFETIME,
    "REFRESH_TOKEN_LIFETIME": environment_variable.REFRESH_TOKEN_LIFETIME,
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
