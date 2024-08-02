from core.conf.environ import env

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.HealthCheckMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not env("DEBUG"):
    pass
    # https://whitenoise.readthedocs.io/en/stable/django.html#enable-whitenoise
    # should be placed directly after the Django SecurityMiddleware
    # MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
