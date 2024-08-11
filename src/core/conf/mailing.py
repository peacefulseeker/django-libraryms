from core.conf.environ import env

EMAIL_BACKEND = env("EMAIL_BACKEND", cast=str, default="django.core.mail.backends.console.EmailBackend")
if env("USE_AWS_SES"):
    EMAIL_BACKEND = "django_ses.SESBackend"

AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID", default=None)
AWS_SES_SECRET_ACCESS_KEY = env("AWS_SES_SECRET_ACCESS_KEY", default=None)
AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME", default=None)
AWS_SES_FROM_EMAIL = env("AWS_SES_FROM_EMAIL", default=None)
