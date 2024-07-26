from datetime import date, timedelta

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.books.const import Language, OrderStatus, ReservationStatus
from apps.users.models import Member
from core.utils.models import TimestampedModel


class ReservationQuerySet(models.QuerySet):
    def reserved_by_member(self, member_id) -> "QuerySet[Reservation]":
        return self.filter(
            member=member_id,
            status__in=[
                ReservationStatus.RESERVED,
                ReservationStatus.ISSUED,
            ],
        )


# TODO: at this point started to think to decouple model CRUD operations from within the models themselves
# perhaps a good idea would be to move the CRUD operations to a separate service layer
# thigh might help also in resolving circular dependency issues, especially actual when model typing is used
class Reservation(TimestampedModel):
    book: "Book"
    member: "Member"
    order: "Order"

    # NOTE: atm. API Only restriction. Admin can still add unlimited reservations to members
    MAX_RESERVATIONS_PER_MEMBER = 5
    DONE_STATES = [
        ReservationStatus.COMPLETED,
        ReservationStatus.CANCELLED,
        ReservationStatus.REFUSED,
    ]

    objects: ReservationQuerySet = models.Manager.from_queryset(ReservationQuerySet)()

    member = models.ForeignKey("users.Member", on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        choices=ReservationStatus,
        max_length=2,
        default=ReservationStatus.RESERVED,
    )
    term = models.DateField(_("Due date"), default=None, blank=True, null=True, help_text=_("Date when reservation expires, 14 days by default"))

    def save(self, *args, **kwargs):
        if self.status == ReservationStatus.ISSUED and self.term is None:
            self.term = Reservation.get_default_term()
        elif self.status in self.DONE_STATES and self.book:
            # TODO: save book reference for history
            self.book.unqueue_next_order()
            self.book.unlink_reservation()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def get_default_term(cls) -> timezone.datetime:
        return timezone.now() + timedelta(days=14)

    @property
    def is_issued(self) -> bool:
        return self.status == ReservationStatus.ISSUED

    @property
    def is_reserved(self) -> bool:
        return self.status == ReservationStatus.RESERVED

    @property
    def overdue_days(self):
        return abs((self.term - timezone.now()).days) if self.term else 0

    @property
    def is_overdue(self) -> bool:
        return self.is_issued and self.overdue_days > 0

    def __str__(self):
        return f"{self.member} - {self.get_status_display()}"


class BookQuerySet(models.QuerySet):
    def available(self) -> "QuerySet[Book]":
        return self.filter(reservation__isnull=True)

    def reserved_by_member(self, member_id) -> "QuerySet[Book]":
        return self.filter(reservation__member=member_id)


class Book(TimestampedModel):
    objects: BookQuerySet = models.Manager.from_queryset(BookQuerySet)()

    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    language = models.CharField(choices=Language, max_length=2)
    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)
    published_at = models.PositiveSmallIntegerField(_("Year of publishing"))
    pages = models.PositiveSmallIntegerField(_("Number of pages"))
    pages_description = models.CharField(_("Extra description for pages"), max_length=100, null=True)
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
        ordering = ["-modified_at"]

    def __str__(self) -> str:
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.create_order_for_reservation()
        return super().save(*args, **kwargs)

    def create_order_for_reservation(self):
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

    def unlink_reservation(self):
        self.reservation = None
        self.save()

    def unqueue_next_order(self):
        if not self.has_orders_in_queue:
            return

        next_order = self.queued_orders.first()
        next_order.status = OrderStatus.UNPROCESSED
        next_order.save()

    def is_issued_to_member(self, member: Member) -> bool:
        if not self.is_issued:
            return False

        return self.reservation.member == member

    def is_reserved_by_member(self, member: Member) -> bool:
        if not self.is_reserved:
            return False

        return self.reservation.member == member

    def is_queued_by_member(self, member: Member) -> bool:
        if not self.is_reserved and not self.is_issued:
            return False

        return self.order_set.filter(member=member, status=OrderStatus.IN_QUEUE).exists()

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
    def reservation_term(self) -> date | None:
        return self.reservation.term if self.is_issued else None

    @property
    def queued_orders(self) -> QuerySet:
        return self.order_set.filter(status=OrderStatus.IN_QUEUE)

    @property
    def has_orders_in_queue(self) -> bool:
        return self.queued_orders.count() >= 1


class OrderQuerySet(models.QuerySet):
    def processable(self, book_id, member_id) -> "QuerySet[Order]":
        return self.filter(
            book=book_id,
            member=member_id,
            status__in=[
                OrderStatus.UNPROCESSED,
                OrderStatus.IN_QUEUE,
                OrderStatus.PROCESSED,
            ],
        )


class Order(TimestampedModel):
    objects: OrderQuerySet = models.Manager.from_queryset(OrderQuerySet)()

    member = models.ForeignKey("users.Member", on_delete=models.SET_NULL, null=True)
    book: Book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True)
    reservation: Reservation = models.OneToOneField(
        Reservation,
        # TODO: not exactly sure whether order should be delted along with reservation
        # seems like better to delete reservation through the order instead. Let's see
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
        "users.User",
        null=True,
        blank=True,
        related_name="+",  # no backwards User relation
        on_delete=models.SET_NULL,
    )

    change_reason = models.CharField(_("Optional comment or change reason"), blank=True, null=True, max_length=100)
    history = HistoricalRecords(
        excluded_fields=["change_reason", "modified_at", "created_at"],
        table_name="books_order_history",
    )

    @property
    def get_status_display(self):
        return self.get_status_display()

    @property
    def _history_user(self):
        return self.last_modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.last_modified_by = value

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.book.is_available:
            self.create_reservation(member=self.member)
        elif self.status == OrderStatus.MEMBER_CANCELLED:
            self.cancel_reservation()
        elif self.status == OrderStatus.REFUSED:
            self.refuse_reservation()
        super().save(*args, **kwargs)

    def cancel(self):
        self.status = OrderStatus.MEMBER_CANCELLED
        self.save()

    def create_reservation(self, member: Member):
        Reservation(member=member, book=self.book, order=self).save()
        self.book.save()

    def cancel_reservation(self):
        if self.reservation is not None:
            self.reservation.status = ReservationStatus.CANCELLED
            self.reservation.save()

    def refuse_reservation(self):
        if self.reservation is not None:
            self.reservation.status = ReservationStatus.REFUSED
            self.reservation.save()

    def delete_reservation(self):
        if self.reservation is not None:
            self.reservation.delete()

    @property
    def in_queue(self) -> bool:
        return self.status == OrderStatus.IN_QUEUE

    @property
    def is_processed(self) -> bool:
        return self.status in [OrderStatus.PROCESSED, OrderStatus.REFUSED, OrderStatus.MEMBER_CANCELLED]

    def __str__(self):
        return f"{self.member} - {self.book} - {self.status}"
