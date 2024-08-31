import uuid

import pytest
from django.utils import timezone
from mixer.backend.django import mixer

from apps.users.models import InvalidPasswordResetTokenError, Librarian, Member, User

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


def test_manager_objects_expected_to_return_group_members_only(librarian_staff, member):
    mixer.blend(User)

    assert User.objects.count() == 3
    assert Librarian.objects.count() == 1
    assert Member.objects.count() == 1


def test_member_registration_code():
    member: Member = mixer.blend(Member)

    assert str(member.uuid.int).startswith(member.registration_code)


class TestPasswordResetToken:
    def test_invalid_by_default(self, member: Member):
        assert not member.password_reset_token
        assert not member.password_reset_token_created_at
        assert not member.is_password_reset_token_valid()

    def test_invalid_raises_when_requested(self, member: Member):
        with pytest.raises(InvalidPasswordResetTokenError) as exc_info:
            member.is_password_reset_token_valid(raise_exception=True)

        assert str(exc_info.value) == "No valid reset token found"

    def test_expired_token_reset(self, member: Member):
        expired_token = member.password_reset_token = uuid.uuid4()
        member.password_reset_token_created_at = timezone.now() - timezone.timedelta(hours=2)
        member.save()

        assert not member.is_password_reset_token_valid()

        member.set_password_reset_token()
        assert member.password_reset_token != expired_token
        assert member.is_password_reset_token_valid()

    def test_expired_token_check_raises_when_requested(self, member: Member):
        member.password_reset_token = uuid.uuid4()
        member.password_reset_token_created_at = timezone.now() - timezone.timedelta(hours=2)
        member.save()

        with pytest.raises(InvalidPasswordResetTokenError) as exc_info:
            member.is_password_reset_token_valid(raise_exception=True)

        assert str(exc_info.value) == "Token has expired"

    def test_valid_token(self, member: Member):
        member.set_password_reset_token()

        assert member.password_reset_token
        assert member.password_reset_token_created_at
        assert member.is_password_reset_token_valid()
