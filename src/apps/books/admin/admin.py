from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from apps.books.models import Author, Book, Publisher, Reservation
from apps.books.models.book import Order, ReservationExtension
from core.utils.admin import ModelAdmin, ReadonlyTabularInline


@admin.display(
    description="Cover preview",
)
def cover_preview(obj: Book) -> str:
    return format_html('<img src="{}" width="150"/>', obj.cover.url)  # pragma: no cover


class BookReservationInline(ReadonlyTabularInline):
    model = Book
    fields = ("title", "author", "published_at", "cover")


class BookInline(BookReservationInline):
    max_num = 10
    extra = 2


class OrderInline(ReadonlyTabularInline):
    fields = ("status", "book", "created_at", "modified_at")
    model = Order


class ReservationExtensionInline(ReadonlyTabularInline):
    fields = ("status", "created_at", "modified_at", "processed_by")
    model = ReservationExtension

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("processed_by")  # pragma: no cover


@admin.register(Book)
class BookAdmin(ModelAdmin, ImportExportModelAdmin):
    search_fields = ("title", "author__first_name", "author__last_name", cover_preview)
    autocomplete_fields = (
        "reservation",
        "author",
        "publisher",
    )

    save_as = True  # allows duplication of the object
    list_select_related = (
        "author",
        "reservation",
        "reservation__member",
    )
    list_display = ("title", "reservation", "author", "published_at", "created_at")
    list_display_links = (
        "title",
        "author",
    )
    readonly_fields = (cover_preview,)


@admin.register(Author)
class AuthorAdmin(ModelAdmin, ImportExportModelAdmin):
    search_fields = ("first_name", "last_name")
    list_display = (
        "__str__",
        "created_at",
    )
    inlines = (BookInline,)


@admin.register(Publisher)
class PublisherAdmin(ModelAdmin, ImportExportModelAdmin):
    search_fields = ("name",)
    list_display = (
        "__str__",
        "city",
        "created_at",
    )

    inlines = (BookInline,)


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    readonly_fields = (
        "created_at",
        "modified_at",
    )
    autocomplete_fields = ("member",)
    search_fields = ("member",)
    list_display = (
        "id",
        "status",
        "member",
        "book",
        "created_at",
        "modified_at",
    )

    list_filter = ("status",)
    list_select_related = ["member", "book"]
    list_display_links = (
        "id",
        "status",
    )

    inlines = (OrderInline, ReservationExtensionInline)

    def has_add_permission(self, request: HttpRequest) -> bool | None:  # pragma: no cover
        """
        New reservations are created either through book orders API or through book object in admin.
        In this case, opening in popup mode assumes it's opened from book item admin or other model admin
        which has a relation with reservation model.
        """
        is_popup = bool(request.GET.get("_popup"))
        return is_popup or None


@admin.register(ReservationExtension)
class ReservationExtensionAdmin(ModelAdmin):
    readonly_fields = (
        "processed_by",
        "reservation",
        "created_at",
        "modified_at",
    )
    list_display = (
        "status",
        "reservation",
        "processed_by",
        "created_at",
        "modified_at",
    )
    list_select_related = [
        "reservation",
        "reservation__member",
        "processed_by",
    ]

    def save_model(self, request: HttpRequest, obj: ReservationExtension, form: Any, change: Any) -> None:
        if form.changed_data:
            obj.processed_by = request.user
        return super().save_model(request, obj, form, change)

    def has_add_permission(self, request: HttpRequest) -> bool:
        "API only creation supported"

        return False  # pragma: no cover
