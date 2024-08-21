from django.urls import path

from apps.users.api.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    MemberProfileView,
    MemberRegistrationRequestView,
)

urlpatterns = [
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("register/", MemberRegistrationRequestView.as_view(), name="member_registration_request"),
    path("me/", MemberProfileView.as_view(), name="member_profile"),
]
