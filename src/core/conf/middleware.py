from core.conf.environ import env

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.healthcheck.HealthCheckMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not env("DEBUG"):
    # https://whitenoise.readthedocs.io/en/stable/django.html#enable-whitenoise
    # should be placed directly after the Django SecurityMiddleware
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

if env("DB_LOGGING_ENABLED", cast=bool, default=False):
    MIDDLEWARE.insert(2, "core.middleware.sql.SqlPrintingMiddleware")
