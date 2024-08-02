from django.shortcuts import render


def app_view(request, *args, **kwargs):
    return render(request, "vue-index.html", context={})
