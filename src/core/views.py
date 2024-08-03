from typing import Any

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.users.api.serializers import CookieTokenRefreshSerializer


class VueAppView(View):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = "vue-index.html"
        self.context = {"props": {}}

    def get_user_data(self, request):
        try:
            access_data = CookieTokenRefreshSerializer(context={"request": request}).validate()
            return access_data
        except Exception:
            pass

        return {}

    def get(self, request, *args, **kwargs):
        self.context["props"].update(**self.get_user_data(request))

        return render(request, self.template_name, context=self.context)
