from datetime import date, timedelta
from typing import Any, Optional

from django.db import models
from django.db.models import Count, Exists, F, OuterRef, Prefetch, Q, QuerySet
from django.db.models.expressions import Case, Value, When
from django.db.models.fields import BooleanField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.books.const import Language, OrderStatus, ReservationExtensionStatus, ReservationStatus
from apps.users.models import Member, User
from core.tasks import send_order_created_email, send_reservation_confirmed_email, send_reservation_extension_approved_email
from core.utils.models import TimestampedModel


class ReservationQuerySet(models.QuerySet):
    def with_extensions(self) -> "ReservationQuerySet":
        return self.prefetch_related("extensions").annotate(
            has_requested_extension=Exists(
                ReservationExtension.objects.filter(
                    reservation=OuterRef("pk"),
                    status=ReservationExtensionStatus.REQUESTED,
                ),
            )
        )

    def with_requested_extensions(self) -> "ReservationQuerySet":
        return self.prefetch_related(
            Prefetch(
                "extensions",
                queryset=ReservationExtension.objects.filter(status=ReservationExtensionStatus.REQUESTED),
                to_attr="requested_extensions",
            ),
        )

    def reserved_by_member(self, member: Member) -> "ReservationQuerySet":
        return self.filter(
            member=member,
            status__in=[
                ReservationStatus.RESERVED,
                ReservationStatus.ISSUED,
            ],
        )


class Reservation(TimestampedModel):
    book: "Book"
    member: "Member"
    order: "Order"
    extensions: "ReservationExtensionQuerySet"

    # annotated
    requested_extensions: "ReservationExtensionQuerySet"
    has_requested_extension: bool

    RESERVATION_TERM = timedelta(days=14)
    MAX_EXTENSIONS_PER_MEMBER = 2
    # NOTE: API Only restriction. Admins can still add unlimited reservations to members
    MAX_RESERVATIONS_PER_MEMBER = 5
    DONE_STATES = [
        ReservationStatus.COMPLETED,
        ReservationStatus.CANCELLED,
        ReservationStatus.REFUSED,
    ]

    objects: ReservationQuerySet = ReservationQuerySet.as_manager()

    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        choices=ReservationStatus,
        max_length=2,
        default=ReservationStatus.RESERVED,
    )
    term = models.DateField(_("Due date"), default=None, blank=True, null=True, help_text=_("Reservation term"))

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.status == ReservationStatus.ISSUED and self.term is None:
            self.term = Reservation.get_default_term()
        elif self.status in self.DONE_STATES and hasattr(self, "book"):
            self.book.process_next_order()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    def extend(self) -> None:
        self.term += self.RESERVATION_TERM
        self.save()

    @classmethod
    def get_default_term(cls) -> date:
        return (timezone.now() + cls.RESERVATION_TERM).date()

    @property
    def extensions_available(self) -> int:
        return self.MAX_EXTENSIONS_PER_MEMBER - self.extensions.count()

    @property
    def is_extendable(self) -> bool:
        return self.is_issued and self.extensions_available > 0

    @property
    def is_issued(self) -> bool:
        return self.status == ReservationStatus.ISSUED

    @property
    def is_reserved(self) -> bool:
        return self.status == ReservationStatus.RESERVED

    @property
    def is_completed(self) -> bool:
        return self.status == ReservationStatus.COMPLETED

    @property
    def overdue_days(self) -> int:
        return abs((self.term - timezone.now()).days) if self.term else 0

    @property
    def is_overdue(self) -> bool:
        return self.is_issued and self.overdue_days > 0

    def __str__(self) -> str:
        return f"{self.pk} - {self.member} - {self.get_status_display()}"


class ReservationExtensionQuerySet(models.QuerySet):
    pass


class ReservationExtension(TimestampedModel):
    objects: ReservationExtensionQuerySet = ReservationExtensionQuerySet.as_manager()

    reservation: Reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="extensions",
    )
    processed_by: User = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    status = models.CharField(
        choices=ReservationExtensionStatus,
        max_length=2,
        default=ReservationExtensionStatus.REQUESTED,
    )

    class Meta:
        ordering = ["-created_at"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._status_initial = self.status

    def status_changed_to(self, status: str) -> bool:
        return self._status_initial != self.status and self.status == status

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.status_changed_to(ReservationExtensionStatus.APPROVED):
            self.reservation.extend()
            send_reservation_extension_approved_email.delay(self.reservation.pk)
        super().save(*args, **kwargs)

        # in case of repetitive instance reuse,
        # makes sure to update the initial status after each save
        self._status_initial = self.status

    def __str__(self) -> str:
        return f"{self.pk} - {self.get_status_display()}"

    def cancel(self) -> None:
        self.status = ReservationExtensionStatus.CANCELLED
        self.save()

    @property
    def reservation_term(self) -> date:
        return self.reservation.term


class BookQuerySet(models.QuerySet):
    def with_reservation(self) -> "BookQuerySet":
        return self.select_related("reservation")

    def with_reservation_member(self) -> "BookQuerySet":
        return self.select_related("reservation__member")

    def with_author(self) -> "BookQuerySet":
        return self.select_related("author")

    def with_publisher(self) -> "BookQuerySet":
        return self.select_related("publisher")

    def with_amount_in_queue(self) -> "BookQuerySet":
        return self.annotate(amount_in_queue=Count("orders", filter=Q(orders__status=OrderStatus.IN_QUEUE)))

    def with_enqueued_by_member(self, member: Member) -> "BookQuerySet":
        subquery = self.filter(orders__member=member, orders__status=OrderStatus.IN_QUEUE).values("id")

        return self.annotate(
            is_enqueued_by_member=Case(When(id__in=subquery, then=Value(True)), default=Value(False), output_field=BooleanField()),
        )

    def with_reservation_extensions(self) -> "BookQuerySet":
        return self.prefetch_related("reservation__extensions").annotate(
            has_requested_extension=Exists(
                ReservationExtension.objects.filter(
                    reservation=OuterRef("reservation__pk"),
                    status=ReservationExtensionStatus.REQUESTED,
                ),
            )
        )

    def available(self) -> "BookQuerySet":
        return self.filter(reservation__isnull=True)

    def reserved_by_member(self, member: Member) -> "BookQuerySet":
        return self.with_reservation_member().filter(reservation__member=member)

    def enqueued_by_member(self, member: Member) -> "BookQuerySet":
        return self.filter(orders__member=member, orders__status=OrderStatus.IN_QUEUE)


class Book(TimestampedModel):
    orders: "QuerySet[Order]"
    objects: BookQuerySet = BookQuerySet.as_manager()

    # annotated
    has_requested_extension: bool

    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey("Author", related_name="books", on_delete=models.CASCADE)
    language = models.CharField(choices=Language, max_length=2)
    publisher = models.ForeignKey("Publisher", related_name="books", on_delete=models.CASCADE)
    published_at = models.PositiveSmallIntegerField(_("Year of publishing"))
    pages = models.PositiveSmallIntegerField(_("Number of pages"))
    pages_description = models.CharField(_("Extra description for pages"), max_length=100, blank=True)
    isbn = models.CharField(max_length=13, verbose_name=_("ISBN"), unique=True)
    reservation: Reservation = models.OneToOneField(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cover = models.ImageField(
        verbose_name=_("Cover image"),
        upload_to="books/covers/",
        blank=True,
        help_text=_("The cover image of book"),
    )

    class Meta:
        ordering = [F("modified_at").desc(nulls_last=True)]

    def __str__(self) -> str:
        return f"{self.title}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.create_order_for_reservation()
        return super().save(*args, **kwargs)

    def create_order_for_reservation(self) -> None:
        """
        Since books can only be created through admin,
        we create the order as processed for consistency
        """
        if self.reservation and not hasattr(self.reservation, "order"):
            Order.objects.create(
                book=self,
                reservation=self.reservation,
                member=self.reservation.member,
                status=OrderStatus.PROCESSED,
            )

    def process_next_order(self) -> None:
        self.reservation = None  # type: ignore[assignment]
        self.save(update_fields=["reservation"])

        if not self.has_enqueued_orders:
            return

        next_order: Order = self.enqueued_orders.first()
        next_order.status = OrderStatus.UNPROCESSED
        next_order.save()
        send_order_created_email.delay(next_order.id)

    def is_issued_to_member(self, member: Member) -> bool:
        if not self.is_issued:
            return False

        return self.reservation.member == member

    def is_reserved_by_member(self, member: Member) -> bool:
        if not self.is_reserved:
            return False

        return self.reservation.member == member

    def is_booked_by_member(self, member: Member) -> bool:
        if not self.is_booked:
            return False

        return self.reservation.member == member

    @property
    def is_available(self) -> bool:
        return self.reservation is None

    @property
    def is_reserved(self) -> bool:
        return self.reservation.is_reserved if self.reservation else False

    @property
    def is_issued(self) -> bool:
        return self.reservation.is_issued if self.reservation else False

    @property
    def is_booked(self) -> bool:
        return self.is_reserved or self.is_issued

    @property
    def reservation_extendable(self) -> bool:
        return self.reservation.is_extendable if self.is_issued else False

    @property
    def reservation_term(self) -> date | None:
        return self.reservation.term if self.is_issued else None

    @property
    def enqueued_orders(self) -> "OrderQuerySet":
        return self.orders.filter(status=OrderStatus.IN_QUEUE).order_by("created_at")

    @property
    def has_enqueued_orders(self) -> bool:
        return self.enqueued_orders.exists()


class OrderQuerySet(models.QuerySet):
    def processed_reserved(self, book: int | Book, member: Member) -> "OrderQuerySet":
        return self.filter(
            book=book,
            member=member,
            status=OrderStatus.PROCESSED,
            reservation__status=ReservationStatus.RESERVED,
        )

    def processable(self, book: int | Book, member: Member) -> "OrderQuerySet":
        return self.filter(
            book=book,
            member=member,
            status__in=[
                OrderStatus.UNPROCESSED,
                OrderStatus.IN_QUEUE,
            ],
        )


class Order(TimestampedModel):
    # NOTE: API Only restriction. Admins can still enqueue ulimited amount of orders to members
    MAX_QUEUED_ORDERS_ALLOWED = 3
    objects: OrderQuerySet = OrderQuerySet.as_manager()

    member = models.ForeignKey(Member, related_name="orders", on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, related_name="orders", on_delete=models.SET_NULL, null=True)
    reservation: Reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=OrderStatus,
        max_length=2,
        default=OrderStatus.UNPROCESSED,
    )
    last_modified_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="+",  # no backwards User relation
        on_delete=models.SET_NULL,
    )

    change_reason = models.CharField(_("Optional comment or change reason"), blank=True, max_length=100)
    history = HistoricalRecords(
        excluded_fields=["change_reason", "modified_at", "created_at"],
        table_name="books_order_history",
    )

    @property
    def _history_user(self) -> Optional[User]:
        return self.last_modified_by

    @_history_user.setter
    def _history_user(self, value: User) -> None:
        self.last_modified_by = value

    class Meta:
        ordering = ["-created_at"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._status_initial = self.status

    def status_changed_to(self, status: str) -> bool:
        return self._status_initial != self.status and self.status == status

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.book.is_available:
            self.create_reservation()
        elif self.status_changed_to(OrderStatus.MEMBER_CANCELLED):
            self.cancel_reservation()
        elif self.status_changed_to(OrderStatus.REFUSED):
            self.refuse_reservation()
        elif self.status_changed_to(OrderStatus.PROCESSED):
            self.notify_member_of_reservation()
        super().save(*args, **kwargs)

        # in case of repetitive instance reuse,
        # makes sure to update the initial status after each save
        self._status_initial = self.status

    def cancel(self) -> None:
        self.status = OrderStatus.MEMBER_CANCELLED
        self.save()

    def create_reservation(self) -> None:
        Reservation(member=self.member, book=self.book, order=self).save()
        self.book.save(update_fields=["reservation"])

    def cancel_reservation(self) -> None:
        if self.reservation is not None:
            self.reservation.status = ReservationStatus.CANCELLED
            self.reservation.save()

    def refuse_reservation(self) -> None:
        if self.reservation is not None:
            self.reservation.status = ReservationStatus.REFUSED
            self.reservation.save()

    def delete_reservation(self) -> None:
        if self.reservation is not None:
            self.reservation.delete()

    def notify_member_of_reservation(self) -> None:
        send_reservation_confirmed_email.delay(self.id, self.reservation.id)

    def __str__(self) -> str:
        return f"{self.pk} - {self.get_status_display()}"
