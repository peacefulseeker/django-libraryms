from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.views.generic.base import RedirectView

api = [
    path("v1/", include("core.urls.api.v1")),
]

urlpatterns = [
    path("api/", include(api), name="api"),
    path("admin/", admin.site.urls, name="admin"),
    path("", RedirectView.as_view(pattern_name="admin:login")),
]
