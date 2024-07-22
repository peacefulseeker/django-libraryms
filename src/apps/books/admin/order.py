from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from apps.books.models import Order
from core.utils.admin import HistoricalModelAdmin


@admin.register(Order)
class OrderAdmin(HistoricalModelAdmin):
    readonly_fields = ("last_modified_by",)
    history_list_display = ("status",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "member",
                    "book",
                    "status",
                    "change_reason",
                    "last_modified_by",
                )
            },
        ),
    )
    list_display = (
        "id",
        "status",
        "member",
        "book",
        "last_modified_by",
        "created_at",
    )

    list_display_links = (
        "id",
        "status",
        "book",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Order are expected to be created by API, initiated by members"""
        return False

    def save_model(self, request: HttpRequest, order: Order, form: Any, change: Any) -> None:
        if form.changed_data:
            order.last_modified_by = request.user
            order._change_reason = form.cleaned_data["change_reason"]
        return super().save_model(request, order, form, change)

    def delete_model(self, request: HttpRequest, order: Order) -> None:
        order.book.delete_reservation()
        return super().delete_model(request, order)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Order]) -> None:
        # TODO: having reservation OneToOne field set on Order instead would simplify things potentially
        for order in queryset:
            order.book.delete_reservation()

        return super().delete_queryset(request, queryset)
