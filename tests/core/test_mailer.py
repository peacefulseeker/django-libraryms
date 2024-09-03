import pytest
from django.core.mail import EmailMessage

from src.core.utils.mailer import HtmlEmailMessage, Mailer, Message


@pytest.fixture
def sample_message():
    return Message(subject="Test Subject", body="Test Body", from_email="from@example.com", to=["to@example.com"], reply_to=["reply@example.com"])


def test_mailer_init(sample_message):
    mailer = Mailer(sample_message)
    assert isinstance(mailer.email, HtmlEmailMessage)

    assert mailer.email.subject == "Test Subject"
    assert mailer.email.body == "Test Body"
    assert mailer.email.from_email == "from@example.com"
    assert mailer.email.to == ["to@example.com"]
    assert mailer.email.reply_to == ["reply@example.com"]


def test_mailer_init_compact_body():
    message = Message(subject="Test Subject", body="  Line 1  \n  Line 2  \n  Line 3  ", from_email="from@example.com", to=["to@example.com"])
    mailer = Mailer(message)

    assert mailer.email.body == "Line 1Line 2Line 3"


def test_mailer_compact_body():
    input_body = """
    This is a test email body.<br/>
    It has multiple lines.
        Some lines have extra indentation.

    There are also empty lines.
    """
    expected_output = "This is a test email body.<br/>It has multiple lines.Some lines have extra indentation.There are also empty lines."

    result = Mailer.compact_body(input_body)
    assert result == expected_output


def test_mailer_send(sample_message, mocker):
    mailer = Mailer(sample_message)
    mock_send = mocker.patch.object(EmailMessage, "send", return_value=1)
    result = mailer.send()

    assert result == 1
    mock_send.assert_called_once()


def test_mailer_send_failure(sample_message, mocker):
    mailer = Mailer(sample_message)
    mock_send = mocker.patch.object(EmailMessage, "send", return_value=0)
    result = mailer.send()

    assert result == 0
    mock_send.assert_called_once()
