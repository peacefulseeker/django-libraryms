import json

import pytest

from src.core.utils.mailer import Mailer, Message


@pytest.fixture
def sample_message() -> Message:
    return Message(
        template_name="SampleTemplate",
        template_data={"sample": "data"},
        from_email="from@example.com",
        to=["to@example.com"],
        reply_to=["reply@example.com"],
    )


@pytest.fixture
def mock_backend(mocker):
    backend = mocker.patch("src.core.utils.mailer.get_connection")
    backend.connection = backend.return_value.connection
    backend.send_templated_email = backend.connection.send_templated_email
    backend.open = backend.return_value.open
    backend.close = backend.return_value.close
    return backend


@pytest.fixture
def mock_sentry_capture_exception(mocker):
    return mocker.patch("src.core.utils.mailer.sentry_sdk.capture_exception")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("src.core.utils.mailer.logger")


def test_send_templated_email(sample_message: Message, mock_backend):
    result = Mailer.send_templated_email(sample_message)

    assert result == 1
    mock_backend.assert_called_once()


def test_send_mass_templated_email(sample_message: Message, mock_backend):
    result = Mailer.send_mass_templated_email([sample_message, sample_message])

    assert result == 2
    mock_backend.assert_called_once()


def test_print_to_console_in_dev_envs(sample_message: Message, mock_backend, mock_logger):
    # console/dummy backends are not expected to have backend connection attribute
    delattr(mock_backend.return_value, "connection")

    Mailer.send_templated_email(sample_message)

    mock_logger.info.assert_called_once_with(f"Sending '{sample_message.template_name}' email to {sample_message.to}")


def test_send_templated_email_with_connection(sample_message: Message, mock_backend, mock_logger):
    result = Mailer.send_templated_email(sample_message)

    assert result == 1
    mock_backend.assert_called_once()
    mock_backend.open.assert_called_once()
    mock_backend.close.assert_called_once()
    mock_backend.send_templated_email.assert_called_with(
        Source=sample_message.from_email,
        Destination={"ToAddresses": sample_message.to},
        ReplyToAddresses=sample_message.reply_to,
        Template=sample_message.template_name,
        TemplateData=json.dumps(sample_message.template_data),
    )
    mock_logger.info.assert_called_once_with(f"Sent '{sample_message.template_name}' email to {sample_message.to}")


def test_mass_templated_email(sample_message: Message, mock_backend):
    result = Mailer.send_mass_templated_email([sample_message, sample_message])

    mock_backend.assert_called_once()
    assert result == 2
    assert mock_backend.send_templated_email.call_count == 2


def test_exception_captured(sample_message: Message, mock_backend, mock_sentry_capture_exception):
    exception = Exception("Could not deliver email")
    mock_backend.send_templated_email.side_effect = exception
    result = Mailer.send_templated_email(sample_message)

    assert result == 0
    mock_sentry_capture_exception.assert_called_once_with(exception)
