from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin


class AppAdminMixin:
    # there's no need to alter these fields from admin
    global_exclude = (
        "created_at",
        "modified_at",
    )

    def get_exclude(self, request, obj=None):
        return (super().get_exclude(request, obj) or ()) + self.global_exclude


class HistoricalModelAdmin(AppAdminMixin, SimpleHistoryAdmin):
    pass


class ModelAdmin(AppAdminMixin, admin.ModelAdmin):
    pass


class StackedInline(AppAdminMixin, admin.StackedInline):
    pass


class TabularInline(AppAdminMixin, admin.TabularInline):
    pass
