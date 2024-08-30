from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.users.api.serializers import CookieTokenRefreshSerializer


class VueAppView(View):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = "vue-index.html"
        self.context: dict[str, dict] = {"props": {}}

    def get_user_data(self, request: HttpRequest) -> dict[str, Any]:
        try:
            access_data = CookieTokenRefreshSerializer(context={"request": request}).validate()
            return access_data
        except Exception:
            pass

        return {}

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.context["props"].update(**self.get_user_data(request))

        return render(request, self.template_name, context=self.context)


def handler404(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    context = {
        "props": {
            "error": {
                "status": 404,
                "message": _(f"Page '{request.path}' not found"),
            }
        }
    }

    return render(request, "vue-index.html", context=context, status=404)
