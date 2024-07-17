import pytest
from mixer.backend.django import mixer

from apps.users.models import Member


@pytest.fixture
def member():
    return mixer.blend(Member)


@pytest.fixture
def another_member():
    return mixer.blend(Member)


# @pytest.fixture
# def librarian():
#     return mixer.blend(Librarian)
