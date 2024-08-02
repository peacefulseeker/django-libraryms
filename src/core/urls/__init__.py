from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.urls.conf import include
from django.views.generic.base import TemplateView

from core.views import app_view

api = [
    path("v1/", include("core.urls.api.v1")),
]

urlpatterns = [
    path("api/", include(api), name="api"),
    path("admin/", admin.site.urls, name="admin"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# important to put at very end to respect patterns above
urlpatterns += [
    path("", app_view, name="app_home"),
    re_path(r"^(?!\/static\/).+", app_view, name="app_routes"),
]
