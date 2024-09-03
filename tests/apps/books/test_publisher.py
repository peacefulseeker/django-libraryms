import pytest
from django.db import IntegrityError
from mixer.backend.django import mixer

from apps.books.models import Publisher

pytestmark = pytest.mark.django_db


def test_publisher_creation():
    publisher = mixer.blend(Publisher)
    assert publisher.name
    assert isinstance(publisher.city, str)


def test_publisher_str_method():
    publisher = mixer.blend(Publisher, name="Test Publisher")
    assert str(publisher) == "Test Publisher"


def test_publisher_name_unique():
    mixer.blend(Publisher, name="Unique Publisher")
    with pytest.raises(IntegrityError):
        mixer.blend(Publisher, name="Unique Publisher")


def test_publisher_city_optional():
    publisher = mixer.blend(Publisher, city="")
    assert publisher.city == ""


def test_publisher_timestamps():
    publisher = mixer.blend(Publisher)
    assert publisher.created_at is not None
    assert publisher.modified_at is None
