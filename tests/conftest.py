import os

import pytest

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


@pytest.fixture(autouse=True, scope="session")
def _create_tmp_index_template():
    # setup
    template_path = "src/core/templates/vue-index.html"
    if os.path.exists(template_path):
        yield
        return

    f = open(template_path, "w")
    yield

    # teardown
    os.remove(f.name)


@pytest.fixture(autouse=True)
def mock_mailer(mocker):
    mocked = mocker.patch("core.tasks.Mailer")
    mocked.return_value.send.return_value = 1
    return mocked
