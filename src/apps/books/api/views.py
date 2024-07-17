from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.books.api.serializers import BookSerializer
from apps.books.const import OrderStatus
from apps.books.models import Book
from apps.books.models import Order as BookOrder
from apps.users.models import Member


# TODO: temporary for quick tests
class TempOverrideUserMixin:
    def _override_auth_member(self, request: Request, pk: int = 3) -> Any:
        member = Member.objects.get(id=pk)
        request.user = member


class BooksViewMixin:
    permission_classes = [AllowAny]
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookListView(BooksViewMixin, generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "author__first_name", "author__last_name"]


class BookDetailView(BooksViewMixin, generics.RetrieveAPIView):
    pass


class BookOrderView(APIView, TempOverrideUserMixin):
    def post(self, request: Request, book_id: int) -> Response:
        # self._override_auth_member(request, pk=4)
        if self._processable_order(book_id, request.user.id).exists():
            return Response(status=400, data={"message": _("Book is already ordered or your order is in queue")})
        order_id, message = self._create_order(book_id, request.user.id)
        return Response({"message": message, "order_id": order_id, "book_id": book_id})

    def delete(self, request: Request, book_id: int) -> Response:
        return self._cancel_order(book_id, request.user.id)

    def _cancel_order(self, member_id: Request, book_id: int) -> Response:
        order = self._processable_order(book_id, member_id)
        if not order.exists():
            return Response(status=400, data={"message": _("No cancellable order found")})
        order = order.get()
        order.status = OrderStatus.MEMBER_CANCELLED
        order.save()

        return Response(status=200, data={"message": _("Order cancelled")})

    def _create_order(self, book_id: int, member_id: int) -> tuple[BookOrder, str]:
        book: Book = get_object_or_404(Book, pk=book_id)
        if book.is_available:
            order_status = OrderStatus.UNPROCESSED
            message = _("Book ordered")
        else:
            order_status = OrderStatus.IN_QUEUE
            message = _("Book order put in queue")

        order: BookOrder = BookOrder.objects.create(book_id=book_id, member_id=member_id, status=order_status)

        return order.id, message

    def _processable_order(self, book_id: int, member_id: int) -> "QuerySet[BookOrder]":
        return BookOrder.objects.processable(member_id, book_id)
