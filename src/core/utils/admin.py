from django.contrib import admin
from django.http import HttpRequest
from simple_history.admin import SimpleHistoryAdmin


class AppAdminMixin:
    show_full_result_count = False  # prevents counting objects twice

    # there's no need to alter these fields from admin
    global_exclude = (
        "created_at",
        "modified_at",
    )

    def get_exclude(self, request: HttpRequest, obj: None = None) -> tuple[str, ...]:
        return (
            *(super().get_exclude(request, obj) or ()),  # type: ignore[misc]
            *self.global_exclude,
        )


class HistoricalModelAdmin(AppAdminMixin, SimpleHistoryAdmin):
    pass


class ModelAdmin(AppAdminMixin, admin.ModelAdmin):
    pass


class StackedInline(AppAdminMixin, admin.StackedInline):
    pass


class TabularInline(AppAdminMixin, admin.TabularInline):
    pass


class ReadonlyTabularInline(TabularInline):
    extra = 0
    show_change_link = True

    def has_change_permission(self, request: HttpRequest, obj: None = None) -> bool:  # pragma: no cover
        return False

    def has_delete_permission(self, request: HttpRequest, obj: None = None) -> bool:  # pragma: no cover
        return False

    def has_add_permission(self, request: HttpRequest, obj: None = None) -> bool:  # pragma: no cover
        return False
