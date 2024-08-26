from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from apps.books.models import Order
from apps.books.models.book import Reservation
from core.utils.admin import HistoricalModelAdmin


@admin.register(Order)
class OrderAdmin(HistoricalModelAdmin):
    readonly_fields = (
        "last_modified_by",
        "reservation",
        "member",
        "book",
    )
    history_list_display = ("status",)
    fields = (
        "member",
        "book",
        "status",
        "reservation",
        "change_reason",
        "last_modified_by",
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request).select_related("reservation", "book", "member", "last_modified_by")
        return qs

    def has_add_permission(self, request: HttpRequest) -> bool:  # pragma: no cover
        """
        Orders are expected to be created by API, initiated by members
        OR when reservation is assigned directly to a book through admin.
        """
        return False

    def save_model(self, request: HttpRequest, order: Order, form: Any, change: Any) -> None:
        if form.changed_data:
            order.last_modified_by = request.user
            order._change_reason = form.cleaned_data["change_reason"]
        return super().save_model(request, order, form, change)

    def delete_model(self, request: HttpRequest, order: Order) -> None:
        order.delete_reservation()
        return super().delete_model(request, order)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[Order]) -> None:
        reservation_ids = [order.reservation.id for order in queryset if order.reservation]
        Reservation.objects.filter(id__in=reservation_ids).delete()

        return super().delete_queryset(request, queryset)
