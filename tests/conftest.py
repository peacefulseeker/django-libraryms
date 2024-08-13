import os

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
