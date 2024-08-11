import environ

from core.conf.common import BASE_DIR

env = environ.Env(
    CI=(bool, False),
    SECRET_KEY=(str, "not-so-secret"),
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(str, ""),
    CSRF_TRUSTED_ORIGINS=(str, ""),
    CORS_ALLOWED_ORIGINS=(str, ""),
    REFRESH_TOKEN_COOKIE_SECURE=(bool, True),
    USE_AWS_S3=(bool, False),
    USE_AWS_SES=(bool, False),
    TIME_ZONE=(str, "Europe/Riga"),
    PRODUCTION_URL=(str, "https://django-libraryms.fly.dev"),
    DATABASE_URL=(str, "sqlite:///db.sqlite3"),
)

if env("CI"):
    envpath = BASE_DIR / ".env.ci"
else:
    envpath = BASE_DIR / ".env"

if envpath.exists():
    env.read_env(envpath)
