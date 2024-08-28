import pytest
from mixer.backend.django import mixer

from apps.users.models import Member


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
