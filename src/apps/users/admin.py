from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User, Member, Librarian

class ModelAdmin(BaseUserAdmin):
    def changelist_view(self, request, extra_context = None):
        has_filters = len(request.GET) > 0
        if has_filters:
            return super().changelist_view(request, extra_context=extra_context)

        return self.filter_by_group(request, extra_context)

    # TODO: try using SimpleListFilter instead
    # https://docs.djangoproject.com/en/5.0/ref/contrib/admin/filters/#using-a-simplelistfilter
    def filter_by_group(self, request, extra_context):
        extra_context = extra_context or {}
        try:
            group = Group.objects.get(name=extra_context.get('group_name'))
            group_filter_parameter = f"groups__id__exact={group.id}"
            return redirect(f"{request.path}?{group_filter_parameter}")
        except (Group.DoesNotExist, Group.MultipleObjectsReturned) as exc:
            print("Could not filter by group", str(exc))
            return super().changelist_view(request, extra_context=extra_context)



@admin.register(Librarian, Member)
class PersonAdmin(ModelAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("groups",)}),
    )
    filter_horizontal = (
        "groups",
    )
    list_display = ("username", "email", "is_staff", "is_active")

    def changelist_view(self, request, extra_context = None):
        extra_context = extra_context or {}
        extra_context.update({
            "group_name": self.model.GROUP_NAME,
        })

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
