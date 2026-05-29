import pytest
import sys
import os
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def setup_modules(mocker):
    # Mock the app module completely before import
    mock_app = MagicMock()
    mock_celery_app = MagicMock()
    # Task decorator returns function unchanged so we can call it directly with self
    mock_celery_app.task = MagicMock(return_value=lambda f: f)
    mock_app.celery_app = mock_celery_app

    # Mock sendgrid modules
    mock_sendgrid = MagicMock()
    mock_sendgrid_helpers = MagicMock()
    mock_sendgrid_helpers_mail = MagicMock()
    mock_sendgrid.SendGridAPIClient = MagicMock()
    mock_sendgrid.helpers = mock_sendgrid_helpers
    mock_sendgrid.helpers.mail = mock_sendgrid_helpers_mail
    mock_sendgrid.helpers.mail.Mail = MagicMock()

    mocker.patch.dict(sys.modules, {
        'app': mock_app,
        'sendgrid': mock_sendgrid,
        'sendgrid.helpers': mock_sendgrid_helpers,
        'sendgrid.helpers.mail': mock_sendgrid_helpers_mail
    })

    # Set default environment variables for happy path
    mocker.patch.dict(os.environ, {
        'SENDGRID_FROM_EMAIL': 'from@example.com',
        'SENDGRID_API_KEY': 'fake-api-key'
    })

    # Import the task after mocking
    from integration-service.src.tasks import sendgrid
    return sendgrid


def test_send_email_success(mocker, setup_modules):
    sendgrid_module = setup_modules
    send_email = sendgrid_module.send_email

    # Configure SendGridAPIClient to return a mock client with successful send
    mock_client = MagicMock()
    mock_client.send.return_value = MagicMock(status_code=202)
    sendgrid_module.SendGridAPIClient.return_value = mock_client

    mock_self = MagicMock()
    result = send_email(mock_self, 'to@example.com', 'Test Subject', 'Hello')
    assert result == 202
    sendgrid_module.SendGridAPIClient.assert_called_once_with('fake-api-key')
    mock_client.send.assert_called_once()


def test_send_email_failure_retry(mocker, setup_modules):
    sendgrid_module = setup_modules
    send_email = sendgrid_module.send_email

    mock_client = MagicMock()
    sendgrid_module.SendGridAPIClient.return_value = mock_client

    # Simulate send failure
    error = Exception("API error")
    mock_client.send.side_effect = error

    mock_self = MagicMock()
    # Celery's retry raises Retry exception; simulate with Exception
    mock_self.retry.side_effect = Exception('Retry')

    with pytest.raises(Exception, match='Retry'):
        send_email(mock_self, 'to@example.com', 'Subject', 'Body')

    # Verify that retry was called with the original exception and countdown
    mock_self.retry.assert_called_once_with(exc=error, countdown=60)


def test_send_email_missing_from_email(mocker, setup_modules):
    sendgrid_module = setup_modules
    send_email = sendgrid_module.send_email

    # Override environment to missing from email (API key still present)
    mocker.patch.dict(os.environ, {
        'SENDGRID_FROM_EMAIL': None,
        'SENDGRID_API_KEY': 'fake-api-key'
    })

    # Simulate Mail raising an exception due to invalid from_email
    sendgrid_module.Mail.side_effect = Exception("Invalid from email")

    mock_self = MagicMock()
    mock_self.retry.side_effect = Exception('Retry')

    with pytest.raises(Exception, match='Retry'):
        send_email(mock_self, 'to@example.com', 'Subject', 'Body')

    # Ensure retry was called and the original exception was the Mail error
    mock_self.retry.assert_called_once()
    assert mock_self.retry.call_args[1]['exc'].args[0] == "Invalid from email"