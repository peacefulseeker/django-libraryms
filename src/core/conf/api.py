from datetime import timedelta

from core.conf.environ import env

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
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_COOKIE_SAMESITE": "strict",
    "REFRESH_TOKEN_COOKIE_NAME": "refresh_token",
    "REFRESH_TOKEN_COOKIE_SECURE": env("REFRESH_TOKEN_COOKIE_SECURE"),
}
