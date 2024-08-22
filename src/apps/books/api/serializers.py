from rest_framework import serializers

from apps.books.models import Author, Book, Publisher, Reservation
from apps.books.models.book import Order
from apps.users.models import User


class SerializerMixin:
    @property
    def user(self) -> User | None:
        return self.context["request"].user if self.context["request"].user.is_authenticated else None


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["first_name", "last_name"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["name"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["status", "term"]


class BookListSerializer(SerializerMixin, serializers.ModelSerializer):
    author = AuthorSerializer()
    cover_image_url = serializers.ImageField(source="cover", use_url=True)

    class Meta:
        model = Book
        ordering = ["-created_at"]
        fields = [
            "id",
            "title",
            "author",
            "cover_image_url",
        ]


class BooksReservedByMemberSerializer(BookListSerializer):
    reservation_id = serializers.SerializerMethodField("get_reservation_id")

    # annotated
    amount_in_queue = serializers.IntegerField()
    is_enqueued_by_member = serializers.BooleanField(default=False)

    class Meta(BookListSerializer.Meta):
        fields = BookListSerializer.Meta.fields + [
            "reservation_id",
            "reservation_term",
            "is_issued",
            "is_enqueued_by_member",
            "amount_in_queue",
        ]

    def get_reservation_id(self, obj: Book) -> int | None:
        if not obj.is_booked_by_member(self.user):
            return None

        return obj.reservation.pk


class BookSerializer(SerializerMixin, serializers.ModelSerializer):
    author = AuthorSerializer()
    publisher = PublisherSerializer()
    language = serializers.CharField(source="get_language_display")
    cover_image_url = serializers.ImageField(source="cover", use_url=True)

    # annotated
    amount_in_queue = serializers.IntegerField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "publisher",
            "published_at",
            "language",
            "isbn",
            "pages",
            "pages_description",
            "cover_image_url",
            "is_available",
            "is_issued",
            "is_reserved",
            "reservation_term",
            "amount_in_queue",
        ]


class BookMemberSerializer(BookSerializer):
    is_issued_to_member = serializers.SerializerMethodField("get_is_issued_to_member")
    is_reserved_by_member = serializers.SerializerMethodField("get_is_reserved_by_member")
    is_max_reservations_reached = serializers.SerializerMethodField("get_is_max_reservations_reached")
    is_max_enqueued_orders_reached = serializers.SerializerMethodField("get_is_max_enqueued_orders_reached")

    # annotated
    amount_in_queue = serializers.IntegerField()
    is_enqueued_by_member = serializers.BooleanField(default=False)

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + [
            "is_issued_to_member",
            "is_reserved_by_member",
            "is_enqueued_by_member",
            "is_max_reservations_reached",
            "is_max_enqueued_orders_reached",
        ]

    def get_is_max_reservations_reached(self, book: Book) -> bool:
        return book.total_reservations_amount >= Reservation.MAX_RESERVATIONS_PER_MEMBER

    def get_is_max_enqueued_orders_reached(self, book: Book) -> bool:
        return book.amount_in_queue >= Order.MAX_QUEUED_ORDERS_ALLOWED

    def get_is_issued_to_member(self, book: Book) -> bool:
        return book.is_issued_to_member(self.user)

    def get_is_reserved_by_member(self, book: Book) -> bool:
        return book.is_reserved_by_member(self.user)
