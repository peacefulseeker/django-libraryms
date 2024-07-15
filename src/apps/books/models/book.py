from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.books.const import Language, OrderStatus, ReservationStatus
from core.utils.models import TimestampedModel


class Reservation(TimestampedModel):
    member = models.ForeignKey("users.Member", on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        choices=ReservationStatus,
        max_length=2,
        default=ReservationStatus.RESERVED,
    )
    term = models.DateTimeField(_("Date, when book should be returned back"), default=None, null=True)

    def save(self, *args, **kwargs):
        if self.status == ReservationStatus.ISSUED:
            self.term = timezone.now() + timedelta(days=14)
        elif self.status in [ReservationStatus.COMPLETED, ReservationStatus.CANCELLED]:
            self.book.process_next_order()
            self.book = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_issued(self) -> bool:
        return self.status == ReservationStatus.ISSUED

    @property
    def overdue_days(self):
        return abs((self.term - timezone.now()).days) if self.term else 0

    @property
    def is_overdue(self) -> bool:
        return self.is_issued and self.overdue_days > 0

    def __str__(self):
        return f"{self.member} - {self.status}"


class Order(TimestampedModel):
    member = models.ForeignKey("users.Member", on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        choices=OrderStatus,
        max_length=2,
        default=OrderStatus.UNPROCESSED,
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # TODO: move to order creator
        if self.book.is_available:
            self.create_reservation()
            # TODO: Send email to administration with link to order/reservation
        super().save(*args, **kwargs)

    def create_reservation(self):
        reservation = Reservation(member=self.member, book=self.book)
        reservation.save()

    def __str__(self):
        return f"{self.member} - {self.book} - {self.status}"


class Book(TimestampedModel):
    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    language = models.CharField(choices=Language, max_length=2)
    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)
    published_at = models.PositiveSmallIntegerField(_("Year of publishing"))
    pages = models.PositiveSmallIntegerField(_("Number of pages"))
    pages_description = models.CharField(_("Extra description for pages"), max_length=100, null=True)
    isbn = models.CharField(max_length=13, verbose_name=_("ISBN"))
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-modified_at"]

    def __str__(self) -> str:
        return f"{self.title}"

    def process_next_order(self):
        if not self.has_members_in_queue:
            return

        next_order = self.queued_orders.first()
        next_order.status = OrderStatus.UNPROCESSED
        self.reservation = next_order.create_reservation()
        self.save()
        next_order.save()

    @property
    def is_available(self):
        return self.reservation is None

    @property
    def queued_orders(self):
        return self.order_set.filter(status=OrderStatus.IN_QUEUE)

    @property
    def has_members_in_queue(self):
        return self.queued_orders.count() >= 1
