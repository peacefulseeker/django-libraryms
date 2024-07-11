from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.models import Librarian, Member, User


@admin.register(Librarian, Member)
class PersonAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("groups",)}),
    )
    filter_horizontal = ("groups",)
    list_display = ("username", "email", "is_staff", "is_active")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({"group_name": self.model.GROUP_NAME})

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(User)
class UseraAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
