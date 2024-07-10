from mixer.backend.django import mixer
import pytest

from apps.users.models import Member, Librarian, User

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("model", "group_name", "group_assigned"),
    [
        (Member, Member.group_name, True),
        (Librarian, Librarian.group_name, True),
        (User, None, False),
    ],
)
def test_model_group_assigned_on_save(model, group_name, group_assigned):
    instance = mixer.blend(model)
    assert instance.group_name == group_name
    assert instance.groups.filter(name=group_name).exists() == group_assigned

