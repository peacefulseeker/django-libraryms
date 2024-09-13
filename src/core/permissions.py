from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class IsSuperUser(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        return bool(request.user and request.user.is_superuser)
