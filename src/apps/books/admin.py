from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from apps.books.models import Author, Book, Order, Publisher, Reservation
from core.utils.admin import ModelAdmin, TabularInline


class AuthorInline(TabularInline):
    model = Author


class BookInline(TabularInline):
    model = Book


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ("title", "reservation", "author", "published_at", "created_at")
    list_display_links = (
        "title",
        "author",
    )
    # instead of Save and add another, Save as new will appear, creating identical object(copying/cloning)
    save_as = True
    search_fields = ("title", "author__first_name", "author__last_name")


@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "created_at",
    )
    search_fields = ("first_name", "last_name")
    inlines = (BookInline,)


@admin.register(Publisher)
class PublisherAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "city",
        "created_at",
    )

    inlines = (BookInline,)

    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        "id",
        "status",
        "member",
        "book",
        "created_at",
    )

    list_display_links = (
        "id",
        "status",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Order are expected to be created by API, initiated by members"""
        return False


class BookStackedInline(TabularInline):
    extra = 0
    fields = ("title", "author", "published_at")
    model = Book
    show_change_link = True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return False

    def has_add_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return False


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    readonly_fields = ("created_at", "modified_at")
    list_display = (
        "id",
        "status",
        "member",
        "book",
        "created_at",
        "modified_at",
    )

    list_display_links = (
        "id",
        "status",
    )

    inlines = (BookStackedInline,)

    def get_form(self, request, obj: Reservation = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["term"].initial = Reservation.get_default_term()
        return form

    def has_add_permission(self, request: HttpRequest, obj: Reservation = None) -> bool:
        """
        New reservations are created either through book orders API or particular book item admin.
        In this case, opening in popup mode assumes it's opened from book item admin or other model admin
        which has a relation with reservation model.
        """
        is_popup = bool(request.GET.get("_popup"))
        if is_popup:
            return True
