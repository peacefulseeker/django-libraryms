from typing import Any

from django.conf import settings
from rest_framework.throttling import AnonRateThrottle as AnonRateThrottleNative
from rest_framework.throttling import BaseThrottle


class ThrottlingMixin(BaseThrottle):
    def allow_request(self, *args: Any, **kwargs: dict[str, Any]) -> bool:
        if settings.DISABLE_THROTTLING:
            return True

        return super().allow_request(*args, **kwargs)


class AnonRateThrottle(ThrottlingMixin, AnonRateThrottleNative):
    pass


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = "password_reset"


class PasswordResetConfirmRateThrottle(AnonRateThrottle):
    scope = "password_reset_confirm"
