from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.users.models import Librarian, Member, User


@admin.register(Librarian, Member)
class PersonAdmin(BaseUserAdmin):
    show_full_result_count = False

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("groups",)}),
    )
    filter_horizontal = ("groups",)
    list_display = ("username", "email", "is_staff", "is_active")

    ordering = ("-date_joined",)

    def get_fieldsets(self, request: HttpRequest, obj: Member | Librarian | None = ...):
        fieldsets = super().get_fieldsets(request, obj)
        if isinstance(obj, Member):
            fieldsets += ((_("Registration"), {"fields": ("registration_code",)}),)
        return fieldsets

    def get_readonly_fields(self, request: HttpRequest, obj: Member | Librarian | None = ...):
        if isinstance(obj, Member):
            return ("registration_code",)
        return ()

    def registration_code(self, obj: Member):
        return obj.registration_code


@admin.register(User)
class UseraAdmin(BaseUserAdmin):
    show_full_result_count = False

    search_fields = ["username", "email"]

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

    ordering = ("-date_joined",)
