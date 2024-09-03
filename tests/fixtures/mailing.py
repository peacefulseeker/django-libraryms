import pytest


@pytest.fixture(autouse=True)
def mock_mailer(mocker):
    mocked = mocker.patch("core.tasks.Mailer")
    mocked.return_value.send.return_value = 1
    return mocked
