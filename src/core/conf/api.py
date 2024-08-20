from datetime import timedelta

from core.conf.environ import env

DISABLE_THROTTLING = env.bool("DISABLE_THROTTLING", default=False)
THROTTLING_ANON_RATE = env.str("THROTTLING_ANON_RATE", default="15/minute")

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
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_COOKIE_SAMESITE": "strict",
    "REFRESH_TOKEN_COOKIE_NAME": "refresh_token",
    "REFRESH_TOKEN_COOKIE_SECURE": env("REFRESH_TOKEN_COOKIE_SECURE"),
}
