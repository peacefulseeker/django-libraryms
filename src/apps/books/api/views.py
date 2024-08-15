from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from apps.books.api.serializers import BookListSerializer, BookMemberSerializer, BookSerializer
from apps.books.const import OrderStatus
from apps.books.models import Book
from apps.books.models import Order as BookOrder
from apps.books.models.book import Order, Reservation
from apps.users.models import Member
from core.tasks import send_order_created_email


class ViewSetMixin:
    request: Request

    @property
    def is_authenticated(self):
        return self.request.user.is_authenticated

    @property
    def query_params(self):
        return self.request.query_params


class BookListView(ViewSetMixin, generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "author__first_name", "author__last_name"]

    def get_queryset(self):
        queryset = Book.objects.with_author().with_reservation()
        get_available = self.query_params.get("available")
        get_reserved_by_me = self.query_params.get("reserved_by_me")
        if get_available is not None:
            return queryset.available()
        elif self.is_authenticated and get_reserved_by_me is not None:
            return queryset.reserved_by_member(self.request.user.id)

        return queryset


class BookDetailView(ViewSetMixin, generics.RetrieveAPIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.is_authenticated:
            return BookMemberSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = Book.objects.with_author().with_publisher()

        if self.is_authenticated:
            return queryset.with_reservation_member()

        return queryset


class BookOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, book_id: int) -> Response:
        if self._get_current_reservations(request.user.id).count() >= Reservation.MAX_RESERVATIONS_PER_MEMBER:
            return Response(status=400, data={"detail": _("Maximum number of reservations reached")})

        if self._processable_order(book_id, request.user.id).exists():
            return Response(status=400, data={"detail": _("Book is already ordered or your order is in queue")})

        order, message = self._create_order(book_id, request.user)
        if order.status == OrderStatus.UNPROCESSED:
            send_order_created_email.delay(order.id)

        return Response({"detail": message, "order_id": order.id, "book_id": book_id})

    def delete(self, request: Request, book_id: int) -> Response:
        return self._cancel_order(book_id, request.user.id)

    def _cancel_order(self, book_id: int, member_id) -> Response:
        try:
            order = self._cancellable_order(book_id, member_id).select_related("book", "reservation").get()
            order.cancel()
        except Order.DoesNotExist:
            return Response(status=400, data={"detail": _("No cancellable order found")})

        return Response(status=HTTP_204_NO_CONTENT)

    def _create_order(self, book_id: int, member: Member) -> tuple[BookOrder, str]:
        book = get_object_or_404(Book, pk=book_id)
        order_status = OrderStatus.UNPROCESSED
        if book.is_available:
            order_status = OrderStatus.UNPROCESSED
            message = _("Book reserved")
        else:
            order_status = OrderStatus.IN_QUEUE
            message = _("Book reservation request put in queue")

        order = BookOrder.objects.create(book=book, member=member, status=order_status)

        return order, message

    def _processable_order(self, book_id: int, member_id: int) -> "QuerySet[BookOrder]":
        return BookOrder.objects.processable(book_id, member_id)

    def _processed_reserved(self, book_id: int, member_id: int) -> "QuerySet[BookOrder]":
        return BookOrder.objects.processed_reserved(book_id, member_id)

    def _cancellable_order(self, book_id: int, member_id: int) -> "QuerySet[BookOrder]":
        return self._processable_order(book_id, member_id) | self._processed_reserved(book_id, member_id)

    def _get_current_reservations(self, member_id: int) -> "QuerySet[Reservation]":
        return Reservation.objects.reserved_by_member(member_id)
