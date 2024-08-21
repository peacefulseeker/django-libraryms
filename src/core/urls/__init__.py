from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.urls.conf import include
from django.views.generic.base import TemplateView

from core.views import VueAppView

urlpatterns = [
    path("api/v1/", include("core.urls.api.v1"), name="api"),
    path("admin/", admin.site.urls, name="admin"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # pragma: no cover

urlpatterns += [
    path("", VueAppView.as_view(), name="app_home"),
    re_path("^(login|books|account|register)", VueAppView.as_view(), name="app_routes"),
]

handler404 = "core.views.handler404"
