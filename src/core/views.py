from django.shortcuts import render


def app_view(request):
    return render(request, "vue-index.html", context={})
