import pytest
from mixer.backend.django import mixer

from apps.users.models import Member


@pytest.fixture
def member():
    member = mixer.blend(Member, username="member", email="member@member.com")
    member.set_password("member")
    member.save()
    return member


@pytest.fixture
def another_member():
    return mixer.blend(Member)
