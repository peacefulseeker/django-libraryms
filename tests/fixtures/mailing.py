from unittest.mock import patch

import pytest


@pytest.fixture
def mock_mailer():
    with patch("core.tasks.Mailer") as MockMailer:
        MockMailer.return_value.send.return_value = 1
        yield MockMailer
