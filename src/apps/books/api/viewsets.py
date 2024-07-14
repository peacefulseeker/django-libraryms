from django.shortcuts import get_object_or_404
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.books.api.serializers import BookSerializer
from apps.books.models import Book


class BookViewMixin:
    permission_classes = [AllowAny]
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookList(BookViewMixin, generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "author__first_name", "author__last_name"]


class BookDetail(BookViewMixin, generics.RetrieveAPIView):
    pass
    # def get(self, request: Request, pk: str) -> Response:
    #     return get_object_or_404(Book, id=pk)
