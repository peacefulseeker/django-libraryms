import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.books.models import Author


@pytest.mark.django_db
class TestAuthor:
    def test_create_author(self):
        author = Author.objects.create(first_name="John", last_name="Doe")
        assert author.first_name == "John"
        assert author.last_name == "Doe"

    def test_author_str_representation(self):
        author = Author(first_name="Jane", last_name="Smith")
        assert str(author) == "Jane Smith"

    def test_author_ordering(self):
        Author.objects.create(first_name="Bob", last_name="Jones")
        Author.objects.create(first_name="Alice", last_name="Brown")

        authors = Author.objects.all()

        assert authors[0].last_name == "Brown"
        assert authors[1].last_name == "Jones"

    def test_unique_author_constraint(self):
        Author.objects.create(first_name="John", last_name="Doe")
        with pytest.raises(IntegrityError):
            Author.objects.create(first_name="John", last_name="Doe")

    def test_year_of_birth_validation(self):
        with pytest.raises(ValidationError):
            author = Author(first_name="Test", last_name="Author", year_of_birth=3000)
            author.full_clean()

    def test_year_of_death_validation(self):
        with pytest.raises(ValidationError):
            author = Author(first_name="Test", last_name="Author", year_of_death=3000)
            author.full_clean()

    def test_birth_death_year_validation(self):
        with pytest.raises(ValidationError):
            author = Author(first_name="Test", last_name="Author", year_of_birth=2000, year_of_death=1999)
            author.full_clean()

    def test_valid_author_with_birth_death_years(self):
        author = Author(first_name="Valid", last_name="Author", year_of_birth=1950, year_of_death=2020)
        author.full_clean()
        author.save()
        assert Author.objects.filter(first_name="Valid", last_name="Author").exists()
