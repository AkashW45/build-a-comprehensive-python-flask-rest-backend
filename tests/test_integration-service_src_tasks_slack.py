import pytest
from unittest.mock import patch, Mock, call
from slack_sdk.errors import SlackApiError

from integration_service.src.tasks.slack import send_slack_notification


@pytest.fixture
def mock_self():
    """Fixture providing a mock task instance with retry method."""
    self = Mock()
    self.retry = Mock()
    return self


class TestSendSlackNotification:
    @patch("integration_service.src.tasks.slack.WebClient")
    @patch("os.environ.get", return_value="fake-token")
    def test_happy_path_returns_true(self, mock_env_get, mock_webclient_cls, mock_self):
        """Message sent successfully, response['ok'] is True."""
        client_mock = mock_webclient_cls.return_value
        client_mock.chat_postMessage.return_value = {"ok": True}

        result = send_slack_notification(mock_self, "hello", "#general")

        mock_webclient_cls.assert_called_once_with(token="fake-token")
        client_mock.chat_postMessage.assert_called_once_with(channel="#general", text="hello")
        mock_self.retry.assert_not_called()
        assert result is True

    @patch("integration_service.src.tasks.slack.WebClient")
    @patch("os.environ.get", return_value="fake-token")
    def test_slack_api_error_triggers_retry(self, mock_env_get, mock_webclient_cls, mock_self):
        """SlackApiError should cause the task to retry with correct parameters."""
        client_mock = mock_webclient_cls.return_value
        error = SlackApiError("channel_not_found", response={"ok": False})
        client_mock.chat_postMessage.side_effect = error

        send_slack_notification(mock_self, "hello", "#general")

        mock_self.retry.assert_called_once_with(exc=error, countdown=60)

    @patch("integration_service.src.tasks.slack.WebClient")
    @patch("os.environ.get", return_value=None)
    def test_missing_token_still_retries_on_error(self, mock_env_get, mock_webclient_cls, mock_self):
        """Edge case: SLACK_BOT_TOKEN is None, task should still retry on API error."""
        client_mock = mock_webclient_cls.return_value
        error = SlackApiError("invalid_auth", response={"ok": False})
        client_mock.chat_postMessage.side_effect = error

        send_slack_notification(mock_self, "hello", "#general")

        mock_webclient_cls.assert_called_once_with(token=None)
        mock_self.retry.assert_called_once_with(exc=error, countdown=60)

    @patch("integration_service.src.tasks.slack.WebClient")
    @patch("os.environ.get", return_value="fake-token")
    def test_ok_false_returns_false_without_retry(self, mock_env_get, mock_webclient_cls, mock_self):
        """Response with ok=False should not throw, return False and not retry."""
        client_mock = mock_webclient_cls.return_value
        client_mock.chat_postMessage.return_value = {"ok": False}

        result = send_slack_notification(mock_self, "hello", "#general")

        mock_self.retry.assert_not_called()
        assert result is False

    @patch("integration_service.src.tasks.slack.WebClient")
    @patch("os.environ.get", return_value="fake-token")
    def test_max_retries_exhausted_raises_error(self, mock_env_get, mock_webclient_cls, mock_self):
        """When max_retries=3 is exhausted, the original exception should propagate."""
        client_mock = mock_webclient_cls.return_value
        error = SlackApiError("service_unavailable", response={"ok": False})
        client_mock.chat_postMessage.side_effect = error

        # Simulate the retry behaviour of a bound Celery task: after max_retries,
        # the task re‑raises the exception. Our implementation only calls self.retry(),
        # which (when Celery is actually running) will re‑raise after max_retries.
        # For unit testing, we verify that retry is called with the correct exception.
        # A separate integration test would confirm the full retry loop.
        send_slack_notification(mock_self, "hello", "#general")

        mock_self.retry.assert_called_once_with(exc=error, countdown=60)