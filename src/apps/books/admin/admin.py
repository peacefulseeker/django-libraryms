from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from apps.books.models import Author, Book, Publisher, Reservation
from apps.books.models.book import Order
from core.utils.admin import ModelAdmin, ReadonlyTabularInline


@admin.display(
    description="Cover preview",
)
def cover_preview(obj):
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


@admin.register(Book)
class BookAdmin(ModelAdmin, ImportExportModelAdmin):
    search_fields = ("title", "author__first_name", "author__last_name", cover_preview)
    autocomplete_fields = [
        "reservation",
        "author",
        "publisher",
    ]

    save_as = True  # allows duplication of the object
    list_select_related = ["author", "reservation", "reservation__member"]
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
        # "member",
        "created_at",
        "modified_at",
    )
    autocomplete_fields = [
        "member",
    ]
    search_fields = ("member",)
    list_display = (
        "id",
        "status",
        "member",
        "book",
        "created_at",
        "modified_at",
    )

    list_select_related = ["member", "book"]
    list_display_links = (
        "id",
        "status",
    )

    inlines = (OrderInline,)

    def has_add_permission(self, request: HttpRequest, obj: Reservation = None) -> bool:  # pragma: no cover
        """
        New reservations are created either through book orders API or particular book item admin.
        In this case, opening in popup mode assumes it's opened from book item admin or other model admin
        which has a relation with reservation model.
        """
        is_popup = bool(request.GET.get("_popup"))
        if is_popup:
            return True
