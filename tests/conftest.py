import django
import pytest

# this allows to run pytest --help / pytest --version without erorrs :shrug:
django.setup()


pytest_plugins = [
    "tests.fixtures.api",
    "tests.fixtures.users",
    "tests.fixtures.books",
]


# speeding up user creation with explicitly set password
@pytest.fixture(autouse=True)
def _use_simple_password_hasher(settings):
    settings.PASSWORD_HASHERS = {
        "django.contrib.auth.hashers.MD5PasswordHasher",
    }


@pytest.fixture(autouse=True)
def mock_mailer(mocker):
    mocked = mocker.patch("core.tasks.Mailer")
    mocked.return_value.send.return_value = 1
    return mocked
