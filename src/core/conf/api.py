from datetime import timedelta

from core.conf.environ import env

DISABLE_THROTTLING = env.bool("DISABLE_THROTTLING", default=False)
THROTTLING_ANON_RATE = env.str("THROTTLING_ANON_RATE", default="15/minute")
THROTTLING_PASSWORD_RESET_RATE = env.str("THROTTLING_PASSWORD_RESET_RATE", default="5/hour")
THROTTLING_PASSWORD_RESET_CONFIRM_RATE = env.str("THROTTLING_PASSWORD_RESET_CONFIRM_RATE", default="5/hour")

REST_FRAMEWORK = {
    "SEARCH_PARAM": "q",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "EXCEPTION_HANDLER": "core.api.exceptions.drf_exception_handler",
    "DEFAULT_THROTTLE_RATES": {
        "anon": THROTTLING_ANON_RATE,
        "password_reset": THROTTLING_PASSWORD_RESET_RATE,
        "password_reset_confirm": THROTTLING_PASSWORD_RESET_CONFIRM_RATE,
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_COOKIE_SAMESITE": "strict",
    "REFRESH_TOKEN_COOKIE_NAME": "refresh_token",
    "REFRESH_TOKEN_COOKIE_SECURE": env("REFRESH_TOKEN_COOKIE_SECURE"),
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Django Library MS API",
    "SERVE_INCLUDE_SCHEMA": False,  # excludes /docs from schema
    "VERSION": "1.0.0",
}
