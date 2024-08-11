import django
import pytest

# this allows to run pytest --help / pytest --version without erorrs :shrug:
django.setup()


pytest_plugins = [
    "tests.fixtures.api",
    "tests.fixtures.users",
    "tests.fixtures.books",
    "tests.fixtures.mailing",
]


# speeding up user creation with explicitly set password
@pytest.fixture(autouse=True)
def use_simple_password_hasher(settings):
    settings.PASSWORD_HASHERS = {
        "django.contrib.auth.hashers.MD5PasswordHasher",
    }
