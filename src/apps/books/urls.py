from django.urls import path

from apps.books.api.viewsets import BookDetail, BookList

urlpatterns = [
    path("", BookList.as_view(), name="books-list"),
    path("<int:pk>", BookDetail.as_view(), name="book-detail"),
]
