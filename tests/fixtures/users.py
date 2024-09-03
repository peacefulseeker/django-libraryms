import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mixer.backend.django import mixer

from apps.books.models.book import ReservationExtension
from apps.users.models import Librarian, Member


@pytest.fixture
def member():
    member = mixer.blend(Member, username="member", email="member@member.com")
    member.raw_password = "member1234"  # for authentication related tests
    member.set_password(member.raw_password)
    member.save()
    return member


@pytest.fixture
def member_with_reset_token(member: Member):
    member.set_password_reset_token()
    return member


@pytest.fixture
def another_member():
    return mixer.blend(Member)


@pytest.fixture(scope="session")
def librarian_group(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        group = Group.objects.get_or_create(name="Librarians")[0]
        content_type = ContentType.objects.get_for_model(ReservationExtension)
        permission = Permission.objects.get(
            codename="change_reservationextension",
            content_type=content_type,
        )
        group.permissions.add(permission)
        return group


@pytest.fixture(scope="session")
def librarian_staff(django_db_setup, django_db_blocker, librarian_group):
    with django_db_blocker.unblock():
        librarian: Librarian = Librarian.objects.get_or_create(username="librarian", email="librarian@librarian.com")[0]
        librarian.groups.add(librarian_group)
        return librarian
