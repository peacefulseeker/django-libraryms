from django.urls import path

from apps.users.api.views import CookieTokenObtainPairView, CookieTokenRefreshView

urlpatterns = [
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
]
