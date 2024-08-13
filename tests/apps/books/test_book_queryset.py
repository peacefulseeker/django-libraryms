import pytest
from mixer.backend.django import mixer

from apps.books.models import Book, Reservation
from apps.users.models import Member


@pytest.mark.django_db
class TestBookQuerySet:
    def test_available(self):
        available_book = mixer.blend(Book)
        reserved_book = mixer.blend(Book)
        mixer.blend(Reservation, book=reserved_book)
        reserved_book.save(update_fields=["reservation"])

        available_books = Book.objects.available()

        assert available_book in available_books
        assert reserved_book not in available_books

    def test_reserved_by_member(self):
        member = mixer.blend(Member)
        reserved_book = mixer.blend(Book)
        mixer.blend(Reservation, book=reserved_book, member=member)
        reserved_book.save(update_fields=["reservation"])
        other_book = mixer.blend(Book)

        member_books = Book.objects.reserved_by_member(member.id)

        assert reserved_book in member_books
        assert other_book not in member_books

    def test_available_with_multiple_books(self):
        available_books = mixer.cycle(3).blend(Book)

        reserved_books = mixer.cycle(2).blend(Book)
        for book in reserved_books:
            book.reservation = mixer.blend(Reservation)
            book.save(update_fields=["reservation"])

        available_queryset = Book.objects.available()

        assert available_queryset.count() == 3
        for book in available_books:
            assert book in available_queryset
        for book in reserved_books:
            assert book not in available_queryset

    def test_reserved_by_member_with_multiple_members(self):
        member1 = mixer.blend(Member)
        member2 = mixer.blend(Member)
        member1_books = mixer.cycle(2).blend(Book)

        for book in member1_books:
            book.reservation = mixer.blend(Reservation, member=member1)
            book.save(update_fields=["reservation"])

        member2_books = mixer.cycle(2).blend(Book)
        for book in member2_books:
            book.reservation = mixer.blend(Reservation, member=member2)
            book.save(update_fields=["reservation"])

        member1_queryset = Book.objects.reserved_by_member(member1.id)

        assert member1_queryset.count() == 2
        for book in member1_books:
            assert book in member1_queryset
        for book in member2_books:
            assert book not in member1_queryset
