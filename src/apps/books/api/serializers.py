from rest_framework import serializers

from apps.books.models import Author, Book, Publisher


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["first_name", "last_name"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["name"]


# TODO: split book list and book detail serializers
# fetch only necessary details for list view
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    publisher = PublisherSerializer()
    language = serializers.CharField(source="get_language_display")

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
        ]
