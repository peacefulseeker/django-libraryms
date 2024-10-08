from typing import Any

from django.http.response import HttpResponseBase
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler


def drf_exception_handler(exc: Exception, context: Any) -> HttpResponseBase:
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        response.data["detail"] = _("Too many requests. Try again later.")

    return response
