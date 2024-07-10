from django.shortcuts import redirect
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User, Member, Librarian

class ModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context = None):
        if len(request.GET) != 0:
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
    def changelist_view(self, request, extra_context = None):
        extra_context = extra_context or {}
        extra_context.update({
            "group_name": self.model.group_name
        })

        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(User, UserAdmin)
