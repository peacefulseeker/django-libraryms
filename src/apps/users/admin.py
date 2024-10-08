from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.models import Librarian, Member, User


class PersonAdmin(BaseUserAdmin):
    show_full_result_count = False
    filter_horizontal = ("groups",)
    list_display: tuple[str, ...] = ("username", "email", "is_active")
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ("-date_joined",)


@admin.register(Member)
class MemberAdmin(PersonAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Registration"),
            {
                "description": "Code that member will receive upon registration request",
                "fields": ("registration_code",),
            },
        ),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("is_active", "groups")}),
    )
    list_display = PersonAdmin.list_display + ("first_name", "last_name")
    readonly_fields = ("registration_code",)


@admin.register(Librarian)
class LibrarianAdmin(PersonAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "groups")}),
    )
    list_display = PersonAdmin.list_display + ("is_staff",)


@admin.register(User)
class UseraAdmin(PersonAdmin):
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

    list_display = PersonAdmin.list_display + ("is_staff", "is_superuser")
