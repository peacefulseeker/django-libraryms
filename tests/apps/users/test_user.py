from mixer.backend.django import mixer
import pytest

from apps.users.models import Member, Librarian, User

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("model", "group_name", "group_assigned"),
    [
        (User, None, False),
        (Member, Member.GROUP_NAME, True),
        (Librarian, Librarian.GROUP_NAME, True),
    ],
)
def test_model_group_assigned_on_save(model, group_name, group_assigned):
    instance = mixer.blend(model)
    assert instance.groups.filter(name=group_name).exists() == group_assigned


@pytest.mark.parametrize(
    ("model", "is_staff"),
    [
        (User, False),
        (Member, False),
        (Librarian, True),
    ],
)
def test_model_is_staff(model, is_staff):
    instance = mixer.blend(model)
    assert instance.is_staff == is_staff

