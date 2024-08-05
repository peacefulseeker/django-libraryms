import django
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.books.models import Author, Book, Languages, Publisher
from apps.users.models import Librarian, Member, User


class Command(BaseCommand):
    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", required=False, help="Dry run mode")

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG:
            print("Not allowed in production envs")
            return

        if options["dry_run"]:
            print("Doing nothing in dry run mode")
            return

        # users
        self.create_super_user()
        self.create_librarian()
        self.create_member()

        # books
        self.create_publisher()
        self.create_author()
        self.create_book()

    def create_super_user(self):
        try:
            user = User.objects.create_superuser(
                username="admin",
                email="admin@admin.com",
                password="admin",
            )
            print(f"Created super user {user.email}")
        except django.db.utils.IntegrityError:
            print("Skipped creating super user as it already exists")

    def create_member(self):
        try:
            member = Member.objects.create_user(
                username="member",
                password="member",
            )
            print(f"Created member {member.username}")
        except django.db.utils.IntegrityError:
            print("Skipped creating member as it already exists")

    def create_librarian(self):
        try:
            librarian = Librarian.objects.create_user(
                username="librarian",
                password="librarian",
            )
            print(f"Created librarian {librarian}")
        except django.db.utils.IntegrityError:
            print("Skipped creating librarian as it already exists")

    def create_publisher(self):
        publisher, created = Publisher.objects.get_or_create(
            name="Худож. лит.",
            city="Москва",
        )
        if created:
            print(f"Created publisher {publisher}")
        else:
            print("Skipped creating publisher as it already exists")

    def create_author(self):
        author, created = Author.objects.get_or_create(
            first_name="Ernest",
            last_name="Hemingway",
            year_of_birth=1890,
            year_of_death=1961,
        )
        if created:
            print(f"Created publisher {author}")
        else:
            print("Skipped creating publisher as it already exists")

    def create_book(self):
        book, created = Book.objects.get_or_create(
            title="Фиеста Прощай, оружие!; Старик и море; Рассказы : : (И восходит солнце) Эрнест Хемингуэй",
            author=Author.objects.last(),
            publisher=Publisher.objects.last(),
            language=Languages.RU,
            published_at=1988,
            pages=448,
            pages_description="с. портр.",
            isbn=5280000108,
        )
        if created:
            print(f"Created book {book}")
        else:
            print("Skipped creating book as it already exists")
