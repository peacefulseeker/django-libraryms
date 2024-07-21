import pytest

pytest_plugins = [
    "tests.fixtures.api",
    "tests.fixtures.users",
    "tests.fixtures.books",
]


# speeding up user creation with explicitly set password
@pytest.fixture(autouse=True)
def use_simple_password_hasher(settings):
    settings.PASSWORD_HASHERS = {
        "django.contrib.auth.hashers.MD5PasswordHasher",
    }
