import pytest
from mixer.backend.django import mixer

from apps.users.models import Librarian, Member, User

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("model", "is_staff", "is_member", "is_librarian"),
    [
        (User, False, False, False),
        (Member, False, True, False),
        (Librarian, True, False, True),
    ],
)
def test_model_properties(model, is_staff, is_member, is_librarian):
    instance = mixer.blend(model)
    assert instance.is_staff == is_staff
    assert instance.is_member == is_member
    assert instance.is_librarian == is_librarian


def test_manager_objects_expected_to_return_group_members_only():
    mixer.blend(User)
    mixer.blend(Librarian)
    mixer.blend(Member)

    assert User.objects.all().count() == 3
    assert Librarian.objects.all().count() == 1
    assert Member.objects.all().count() == 1
