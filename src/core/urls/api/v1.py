from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from core.urls.api.views import AuthenticatedSpectacularSwaggerView

urlpatterns = [
    path("auth/", include("apps.users.urls.auth")),
    path("books/", include("apps.books.urls")),
    path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/swagger/", AuthenticatedSpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
