from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase


class HealthCheckMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        if request.path == "/healthz":
            return HttpResponse("ok")
        return self.get_response(request)
