from django.db import models
from django.db.models import QuerySet

from apps.books.const import OrderStatus
from apps.books.models.book import Book
from core.utils.models import TimestampedModel


class OrderQuerySet(models.QuerySet):
    def processable(self, member_id, book_id) -> "QuerySet[Order]":
        return self.filter(book=book_id, member=member_id, status__in=[OrderStatus.UNPROCESSED, OrderStatus.IN_QUEUE])


class Order(TimestampedModel):
    objects: OrderQuerySet = models.Manager.from_queryset(OrderQuerySet)()

    member = models.ForeignKey("users.Member", on_delete=models.SET_NULL, null=True)
    book: Book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        choices=OrderStatus,
        max_length=2,
        default=OrderStatus.UNPROCESSED,
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.book.is_available:
            self.book.create_reservation(member=self.member)
        elif self.status == OrderStatus.MEMBER_CANCELLED:
            self.book.cancel_reservation()
        elif self.status == OrderStatus.REFUSED:
            self.book.refuse_reservation()
        super().save(*args, **kwargs)

    def cancel(self):
        self.status = OrderStatus.MEMBER_CANCELLED
        self.save()

    @property
    def in_queue(self) -> bool:
        return self.status == OrderStatus.IN_QUEUE

    @property
    def is_processed(self) -> bool:
        return self.status in [OrderStatus.PROCESSED, OrderStatus.REFUSED, OrderStatus.MEMBER_CANCELLED]

    def __str__(self):
        return f"{self.member} - {self.book} - {self.status}"
