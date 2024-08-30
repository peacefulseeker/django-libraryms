from datetime import date
from typing import Any

from django.apps import apps as django_apps
from django.contrib import admin
from django.db.models import Model, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.users.models import User
from core.utils.admin import ModelAdmin

HistoricalOrder: HistoricalRecords = django_apps.get_model("books", "HistoricalOrder")
HistoricalOrder._meta.verbose_name = _("Deleted order")
HistoricalOrder._meta.verbose_name_plural = _("Deleted orders")


@admin.display(
    description="id",
)
def history_id(obj: Model) -> int:  # pragma: no cover
    return obj.id


@admin.display(
    description="status",
)
def history_type(obj: Model) -> str:  # pragma: no cover
    return obj.get_history_type_display()


@admin.display(
    description="date of deletion",
)
def history_date(obj: Model) -> date:  # pragma: no cover
    return obj.history_date


@admin.display(
    description="reason/comment",
)
def history_change_reason(obj: Model) -> str:  # pragma: no cover
    return obj.history_change_reason


@admin.display(
    description="performed by",
)
def history_user(obj: Model) -> User:  # pragma: no cover
    return obj.history_user


@admin.register(HistoricalOrder)
class DeletedOrderAdmin(ModelAdmin):
    readonly_fields = [field.name for field in HistoricalOrder._meta.get_fields()]

    list_select_related = ["member", "book", "history_user"]
    list_display = (
        history_id,
        history_type,
        history_change_reason,
        history_date,
        "book",
        "member",
        history_user,
    )
    search_fields = (
        "book__title",
        "history_user__username",
    )

    list_display_links = (history_id, history_type)

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:  # pragma: no cover
        return False

    def has_add_permission(self, request: HttpRequest) -> bool:  # pragma: no cover
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[HistoricalRecords]:
        return super().get_queryset(request).filter(history_type="-")
