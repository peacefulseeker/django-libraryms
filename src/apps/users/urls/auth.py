from django.urls import path

from apps.users.api.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    MemberPasswordChange,
    MemberPasswordReset,
    MemberPasswordResetConfirm,
    MemberProfileView,
    MemberRegistrationRequestView,
)

urlpatterns = [
    path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("register/", MemberRegistrationRequestView.as_view(), name="member_registration_request"),
    path("me/", MemberProfileView.as_view(), name="member_profile"),
    path("password/change/", MemberPasswordChange.as_view(), name="member_password_change"),
    path("password/reset/", MemberPasswordReset.as_view(), name="member_password_reset"),
    path("password/reset-confirm/", MemberPasswordResetConfirm.as_view(), name="member_password_reset_confirm"),
]
