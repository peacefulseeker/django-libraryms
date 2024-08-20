from django.conf import settings
from rest_framework.throttling import AnonRateThrottle as AnonRateThrottleNative
from rest_framework.throttling import BaseThrottle


class ThrottlingMixin(BaseThrottle):
    def allow_request(self, request, view):
        if settings.DISABLE_THROTTLING:
            return True

        return super().allow_request(request, view)


class AnonRateThrottle(ThrottlingMixin, AnonRateThrottleNative):
    pass
