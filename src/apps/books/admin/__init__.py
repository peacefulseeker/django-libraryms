from apps.books.admin.admin import AuthorAdmin, BookAdmin, PublisherAdmin, ReservationAdmin
from apps.books.admin.deleted_order import DeletedOrderAdmin
from apps.books.admin.order import OrderAdmin

__all__ = [
    "AuthorAdmin",
    "BookAdmin",
    "PublisherAdmin",
    "ReservationAdmin",
    "OrderAdmin",
    "DeletedOrderAdmin",
]
