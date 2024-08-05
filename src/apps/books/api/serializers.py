from rest_framework import serializers

from apps.books.models import Author, Book, Publisher, Reservation


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


class BookListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    cover_image_url = serializers.ImageField(source="cover", use_url=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "pages",
            "cover_image_url",
            "is_available",
            # reservations specific
            "reservation_term",
            "is_issued",
        ]


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    publisher = PublisherSerializer()
    language = serializers.CharField(source="get_language_display")
    cover_image_url = serializers.ImageField(source="cover", use_url=True)
    is_issued_to_member = serializers.SerializerMethodField("get_is_issued_to_member")
    is_reserved_by_member = serializers.SerializerMethodField("get_is_reserved_by_member")
    is_queued_by_member = serializers.SerializerMethodField("get_is_queued_by_member")
    max_reservations_reached = serializers.SerializerMethodField("get_max_reservations_reached")

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
            "is_available",
            "is_issued",
            "is_reserved",
            "reservation_term",
            "cover_image_url",
            "is_issued_to_member",
            "is_queued_by_member",
            "is_reserved_by_member",
            "max_reservations_reached",
        ]

    @property
    def user(self):
        return self.context["request"].user if self.context["request"].user.is_authenticated else None

    def get_max_reservations_reached(self, obj: Book) -> int | None:
        if not self.user:
            return None

        return Reservation.objects.reserved_by_member(self.user.id).count() >= Reservation.MAX_RESERVATIONS_PER_MEMBER

    def get_is_issued_to_member(self, obj: Book) -> bool:
        if not self.user:
            return False

        return obj.is_issued_to_member(self.user)

    def get_is_reserved_by_member(self, obj: Book) -> bool:
        if not self.user:
            return False

        return obj.is_reserved_by_member(self.user)

    def get_is_queued_by_member(self, obj: Book) -> bool:
        if not self.user:
            return False

        return obj.is_queued_by_member(self.user)
