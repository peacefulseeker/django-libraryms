from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from apps.users.api.views import CookieTokenObtainPairView, CookieTokenRefreshView

urlpatterns = [
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
