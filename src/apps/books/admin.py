from django.contrib import admin

# from django.utils.translation import gettext_lazy as _
from apps.books.models import Author, Book, Publisher
from core.utils.admin import ModelAdmin, TabularInline


class AuthorInline(TabularInline):
    model = Author


class BookInline(TabularInline):
    model = Book


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ("title", "author", "published_at", "created_at")
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
