from gettext import ngettext

from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import filters, generics, serializers
from rest_framework import status as status_codes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.books.api.serializers import (
    BookEnqueuedByMemberSerializer,
    BookListSerializer,
    BookMemberSerializer,
    BookSerializer,
    BooksReservedByMemberSerializer,
    DetailInlineSerializer,
)
from apps.books.const import OrderStatus
from apps.books.models import Book
from apps.books.models import Order as BookOrder
from apps.books.models.book import BookQuerySet, Order, Reservation, ReservationExtension
from apps.users.models import Member
from core.tasks import send_extension_request_received_email, send_order_created_email


class ViewSetMixin:
    request: Request

    @property
    def is_authenticated(self) -> bool:
        return self.request.user.is_authenticated

    @property
    def query_params(self) -> dict[str, str]:
        return self.request.query_params


class BookListView(ViewSetMixin, generics.ListAPIView):
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "author__first_name", "author__last_name"]

    def show_reserved_by_member(self) -> bool:
        return self.is_authenticated and self.query_params.get("reserved_by_me") is not None

    def show_enqueued_by_member(self) -> bool:
        return self.is_authenticated and self.query_params.get("enqueued_by_me") is not None

    def get_serializer_class(self) -> type[BookListSerializer | BookMemberSerializer | BooksReservedByMemberSerializer]:
        if self.show_reserved_by_member():
            return BooksReservedByMemberSerializer
        elif self.show_enqueued_by_member():
            return BookEnqueuedByMemberSerializer
        return BookListSerializer

    def get_queryset(self) -> BookQuerySet:
        queryset = Book.objects.with_author().with_reservation().with_amount_in_queue()
        if self.query_params.get("available") is not None:
            return queryset.available()
        elif self.show_reserved_by_member():
            return queryset.with_reservation_extensions().reserved_by_member(self.request.user)
        elif self.show_enqueued_by_member():
            return queryset.enqueued_by_member(self.request.user)
        return queryset


class BookDetailView(ViewSetMixin, generics.RetrieveAPIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self) -> type[BookSerializer | BookMemberSerializer]:
        if self.is_authenticated:
            return BookMemberSerializer
        return BookSerializer

    def get_queryset(self) -> BookQuerySet:
        queryset = Book.objects.with_author().with_publisher().with_amount_in_queue().with_reservation()

        if self.is_authenticated:
            return queryset.with_reservation_member().with_enqueued_by_member(self.request.user)

        return queryset


@extend_schema(
    request=None,
)
class BookOrderView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="book_order_create",
        responses={
            status_codes.HTTP_200_OK: OpenApiResponse(
                inline_serializer(
                    "BookOrderSuccessSerializer",
                    fields={
                        "detail": serializers.CharField(),
                        "book_id": serializers.IntegerField(),
                        "order_id": serializers.IntegerField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Book reserved",
                        value={
                            "detail": "Order created and book reserved",
                            "book_id": 1,
                            "order_id": 1,
                        },
                    ),
                    OpenApiExample(
                        "Book put in queue",
                        value={
                            "detail": "Order created and put in queue",
                        },
                    ),
                ],
            ),
            status_codes.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=DetailInlineSerializer,
                examples=[
                    OpenApiExample(
                        "Book is not available",
                        value={
                            "detail": "Book is not available",
                        },
                    ),
                    OpenApiExample(
                        "Maximum number of reservations reached",
                        value={
                            "detail": "Maximum number of reservations reached",
                        },
                    ),
                    OpenApiExample(
                        "Book is already reserved",
                        value={
                            "detail": "Book is already reserved",
                        },
                    ),
                    OpenApiExample(
                        "Book is already in queue",
                        value={
                            "detail": "Book is already in queue",
                        },
                    ),
                ],
            ),
        },
    )
    def post(self, request: Request, book_id: int) -> Response:
        """
        Places a book order and reserves it for for an authenticated member if books is available,
        otherwise places an order to a book queue.
        """

        if self._max_reservations_reached(request.user):
            return Response(status=status_codes.HTTP_400_BAD_REQUEST, data={"detail": _("Maximum number of reservations reached")})

        book = get_object_or_404(Book, pk=book_id)

        if self._processable_order(book, request.user).exists():
            return Response(status=status_codes.HTTP_400_BAD_REQUEST, data={"detail": _("Book is already ordered or your order is in queue")})

        if self._max_enqueued_orders_reached(book):
            return Response(status=status_codes.HTTP_400_BAD_REQUEST, data={"detail": _("Maximum number of orders in queue reached")})

        order, message = self._create_order(book, request.user)
        if order.status == OrderStatus.UNPROCESSED:
            send_order_created_email.delay(order.id)

        return Response({"detail": message, "order_id": order.id, "book_id": book_id})

    @extend_schema(
        operation_id="book_order_cancel",
        responses={
            status_codes.HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Reservation cancelled",
            ),
            status_codes.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=DetailInlineSerializer,
                description="No cancellable order found",
            ),
        },
    )
    def delete(self, request: Request, book_id: int) -> Response:
        """
        Cancels a book reservation or order for a authenticated member
        if cancellable order exists.
        """

        return self._cancel_order(book_id, request.user)

    def _cancel_order(self, book_id: int, member: Member) -> Response:
        try:
            order = self._cancellable_order(book_id, member).select_related("book", "reservation").get()
            order.cancel()
        except Order.DoesNotExist:
            return Response(status=status_codes.HTTP_404_NOT_FOUND, data={"detail": _("No cancellable order found")})

        return Response(status=status_codes.HTTP_204_NO_CONTENT)

    def _create_order(self, book: Book, member: Member) -> tuple[BookOrder, str]:
        order_status = OrderStatus.UNPROCESSED
        if book.is_available:
            order_status = OrderStatus.UNPROCESSED
            message = _("Book reserved")
        else:
            order_status = OrderStatus.IN_QUEUE
            message = _("Book reservation request put in queue")

        with transaction.atomic():
            if book.is_available:
                book = Book.objects.select_for_update().get(pk=book.id)
            order = BookOrder.objects.create(book=book, member=member, status=order_status)

        return order, message

    def _processable_order(self, book: int | Book, member: Member) -> "QuerySet[BookOrder]":
        return BookOrder.objects.processable(book, member)

    def _processed_reserved(self, book_id: int, member: Member) -> "QuerySet[BookOrder]":
        return BookOrder.objects.processed_reserved(book_id, member)

    def _cancellable_order(self, book_id: int | Book, member: Member) -> "QuerySet[BookOrder]":
        return self._processable_order(book_id, member) | self._processed_reserved(book_id, member)

    def _max_reservations_reached(self, member: Member) -> bool:
        return Reservation.objects.reserved_by_member(member).count() >= Reservation.MAX_RESERVATIONS_PER_MEMBER

    def _max_enqueued_orders_reached(self, book: Book) -> bool:
        return book.enqueued_orders.count() >= Order.MAX_QUEUED_ORDERS_ALLOWED


@extend_schema(
    request=None,
)
class BookReservationExtendView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="request_reservation_extension",
        responses={
            status_codes.HTTP_200_OK: OpenApiResponse(
                response=DetailInlineSerializer,
                description="Reservation extended",
            ),
            status_codes.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=DetailInlineSerializer,
                examples=[
                    OpenApiExample(
                        "Extension already requested",
                        value={
                            "detail": "Reservation extension already requested",
                        },
                    ),
                    OpenApiExample(
                        "Can not be extended",
                        value={
                            "detail": "Reservation cannot be extended",
                        },
                    ),
                ],
            ),
        },
    )
    def post(self, request: Request, book_id: int) -> Response:
        """
        Requests a reservation extension for for current member book reservation.
        """
        try:
            reservation: Reservation = Reservation.objects.with_extensions().get(book=book_id, member=request.user)
        except Reservation.DoesNotExist:
            return Response(status=status_codes.HTTP_404_NOT_FOUND, data={"detail": _("No reservation found")})

        if reservation.has_requested_extension:
            return Response(status=status_codes.HTTP_400_BAD_REQUEST, data={"detail": _("Reservation extension already requested")})

        if not reservation.is_extendable:
            return Response(status=status_codes.HTTP_400_BAD_REQUEST, data={"detail": _("Reservation cannot be extended")})

        extension = ReservationExtension.objects.create(reservation=reservation)
        send_extension_request_received_email.delay(extension.id)

        return Response(status=status_codes.HTTP_200_OK, data={"detail": _("Reservation extension requested")})

    @extend_schema(
        operation_id="cancel_reservation_extension",
        responses={
            status_codes.HTTP_200_OK: OpenApiResponse(
                response=DetailInlineSerializer,
                description="Reservation extension cancelled",
                examples=[
                    OpenApiExample(
                        "No more extensions left",
                        value={
                            "detail": "You have no more extensions available for this book",
                        },
                    ),
                    OpenApiExample(
                        "1 extension left",
                        value={
                            "detail": "You have 1 more extension available for this book",
                        },
                    ),
                ],
            ),
            status_codes.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=DetailInlineSerializer,
                description="No cancellable reservation extension found",
            ),
        },
    )
    def delete(self, request: Request, book_id: int) -> Response:
        try:
            reservation: Reservation = Reservation.objects.with_requested_extensions().get(book=book_id, member=request.user)
        except Reservation.DoesNotExist:
            return Response(status=status_codes.HTTP_404_NOT_FOUND, data={"detail": _("No reservation found")})

        if not reservation.requested_extensions:
            return Response(status=status_codes.HTTP_400_BAD_REQUEST, data={"detail": _("No cancellable reservation extension found")})

        requested_extension: ReservationExtension = reservation.requested_extensions[0]
        requested_extension.cancel()

        extensions_available = reservation.extensions_available
        if extensions_available:
            detail = ngettext(
                "You have %(extensions)d more extension available for this book",
                "You have %(extensions)d more extensions available for this book",
                extensions_available,
            ) % {
                "extensions": extensions_available,
            }
        else:
            detail = _("You have no more extensions available for this book")

        return Response(status=status_codes.HTTP_200_OK, data={"detail": detail})
