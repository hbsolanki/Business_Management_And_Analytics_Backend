from bma.config import environment_variable

#Email
# EMAIL_BACKEND = env(
#     "EMAIL_BACKEND",
#     default="django.core.mail.backends.console.EmailBackend",
# )
# SMTP config
EMAIL_HOST = environment_variable.EMAIL_HOST
EMAIL_PORT = environment_variable.EMAIL_PORT
EMAIL_USE_TLS = environment_variable.EMAIL_USE_TLS

EMAIL_HOST_USER = environment_variable.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD =environment_variable.EMAIL_HOST_PASSWORD

DEFAULT_FROM_EMAIL = environment_variable.DEFAULT_FROM_EMAIL
