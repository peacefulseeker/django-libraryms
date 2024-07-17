from django.urls import path

from apps.books.api.views import BookDetailView, BookListView, BookOrderView

urlpatterns = [
    path("", BookListView.as_view(), name="books-list"),
    path("<int:pk>", BookDetailView.as_view(), name="book-detail"),
    path("<int:book_id>/order/", BookOrderView.as_view(), name="book-order"),
]
