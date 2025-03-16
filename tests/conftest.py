import sys

import pytest

# When running any of the following commands, we skip loading any fixtures
# which usually lead to unwanted django setup related issues
if not any(arg in sys.argv for arg in ['--help', '--version', '-h']):
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
    mocked.send_templated_email.return_value = 1
    return mocked
