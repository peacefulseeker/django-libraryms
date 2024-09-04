from functools import cached_property
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.users.api.serializers import CookieTokenRefreshSerializer
from core.conf.environ import env


class ViewMixin:
    template_name: str = "vue-index.html"

    @cached_property
    def frontend_assets_url(self) -> str:
        if env("FRONTEND_ASSETS_VERSION"):
            return f"https://{env('AWS_S3_CUSTOM_DOMAIN')}/v/{env('FRONTEND_ASSETS_VERSION')}/"
        return "/static/frontend/"


class VueAppView(View, ViewMixin):
    def get_user_data(self, request: HttpRequest) -> dict[str, Any]:
        try:
            access_data = CookieTokenRefreshSerializer(context={"request": request}).validate()
            return access_data
        except Exception:
            pass

        return {}

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = {
            "FRONTEND_ASSETS_URL": self.frontend_assets_url,
            "props": {**self.get_user_data(request)},
        }

        return render(request, self.template_name, context=context)


class Handler404(View, ViewMixin):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = {
            "FRONTEND_ASSETS_URL": self.frontend_assets_url,
            "props": {
                "error": {
                    "status": 404,
                    "message": _(f"Page '{request.path}' not found"),
                }
            },
        }
        return render(request, self.template_name, context=context, status=404)
