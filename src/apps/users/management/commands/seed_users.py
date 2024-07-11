from django.core.management.base import BaseCommand

from apps.users.models import Librarian, Member, User


class Command(BaseCommand):
    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true", required=False, help="Dry run mode")

    def handle(self, *args, **options) -> None:
        if options["dry_run"]:
            print("Dry run mode")
            return

        self.create_super_user()
        self.create_librarians()
        self.create_members()

    def create_super_user(self):
        # TODO: only in dev envs
        user = User.objects.create_superuser(
            username="admin",
            email="admin@admin.com",
            password="admin",
        )
        print(f"Created super user {user.email}")

    def create_members(self):
        member = Member.objects.create_user(
            username="member",
            password="member",
        )
        print(f"Created member {member}")

    def create_librarians(self):
        librarian = Librarian.objects.create_user(
            username="librarian",
            password="librarian",
        )
        print(f"Created librarian {librarian}")
