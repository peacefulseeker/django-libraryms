import pytest

pytestmark = pytest.mark.django_db


def test_timestamped_model_creation(book):
    assert book.created_at is not None
    assert book.modified_at is None


def test_timestamped_model_update(book):
    initial_created_at = book.created_at

    book.save()

    assert book.created_at == initial_created_at
    assert book.modified_at is not None
    assert book.modified_at > book.created_at


def test_timestamped_model_changed_property(book):
    assert not book.changed

    book.save()
    assert book.changed


def test_timestamped_model_multiple_updates(book):
    book.save()
    first_modified_at = book.modified_at

    book.save()
    second_modified_at = book.modified_at
    assert second_modified_at > first_modified_at

    book.save()
    assert book.modified_at > second_modified_at
