import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationStatus
from apps.books.models import Book, Reservation
from apps.users.models import Member


@pytest.mark.django_db
class TestReservationQuerySet:
    def test_reserved_by_member(self):
        member = mixer.blend(Member)
        reserved_book = mixer.blend(Book)
        issued_book = mixer.blend(Book)
        completed_book = mixer.blend(Book)

        mixer.blend(Reservation, member=member, book=reserved_book, status=ReservationStatus.RESERVED)
        mixer.blend(Reservation, member=member, book=issued_book, status=ReservationStatus.ISSUED)
        mixer.blend(Reservation, member=member, book=completed_book, status=ReservationStatus.COMPLETED)

        reservations = Reservation.objects.reserved_by_member(member.id)

        assert reservations.count() == 2
        assert reserved_book.reservation in reservations
        assert issued_book.reservation in reservations
        assert completed_book.reservation not in reservations

    def test_reserved_by_member_with_multiple_members(self):
        member1 = mixer.blend(Member)
        member2 = mixer.blend(Member)

        member1_reservations = mixer.cycle(2).blend(Reservation, member=member1, status=ReservationStatus.RESERVED)
        member2_reservations = mixer.cycle(2).blend(Reservation, member=member2, status=ReservationStatus.RESERVED)

        reservations = Reservation.objects.reserved_by_member(member1.id)

        assert reservations.count() == 2
        for reservation in member1_reservations:
            assert reservation in reservations
        for reservation in member2_reservations:
            assert reservation not in reservations

    def test_reserved_by_member_with_various_statuses(self):
        member = mixer.blend(Member)
        statuses = [
            ReservationStatus.RESERVED,
            ReservationStatus.ISSUED,
            ReservationStatus.COMPLETED,
            ReservationStatus.CANCELLED,
            ReservationStatus.REFUSED,
        ]

        reservations = [mixer.blend(Reservation, member=member, status=status) for status in statuses]

        member_reservations = Reservation.objects.reserved_by_member(member.id)

        assert member_reservations.count() == 2
        assert reservations[0] in member_reservations  # RESERVED
        assert reservations[1] in member_reservations  # ISSUED
        assert reservations[2] not in member_reservations  # COMPLETED
        assert reservations[3] not in member_reservations  # CANCELLED
        assert reservations[4] not in member_reservations  # REFUSED
