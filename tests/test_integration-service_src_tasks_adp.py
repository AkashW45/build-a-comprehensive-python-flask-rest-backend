import pytest
from unittest.mock import patch, MagicMock
import requests

# Import the task and the Celery app (if needed)
from integration_service.src.tasks.adp import sync_payroll, celery_app


class TestSyncPayroll:
    """Tests for the ADP payroll sync Celery task."""

    @pytest.fixture
    def mock_request(self):
        """Fixture to mock requests.post/get."""
        with patch('integration_service.src.tasks.adp.requests') as mock_req:
            yield mock_req

    @pytest.fixture
    def mock_env_adp_url(self):
        """Fixture to set a valid ADP_API_URL."""
        with patch.dict('os.environ', {'ADP_API_URL': 'https://adp.example.com/payroll'}):
            yield

    def test_sync_payroll_success(self, mock_request, mock_env_adp_url):
        """Happy path: the ADP API call succeeds and the task returns 'synced'."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.post.return_value = mock_response

        # The task currently only returns a placeholder; we simulate full call.
        result = sync_payroll.run(payroll_run_id='123')

        assert result == {'status': 'synced'}
        # Ensure the API was called with the right URL and payload
        mock_request.post.assert_called_once_with(
            'https://adp.example.com/payroll',
            json={'payroll_run_id': '123'}  # placeholder
        )

    def test_sync_payroll_api_failure_retries(self, mock_request, mock_env_adp_url):
        """When the ADP API raises a request exception, the task should retry."""
        mock_request.post.side_effect = requests.exceptions.RequestException("ADP API down")

        # Mock the task's retry method to avoid actual Celery retry
        with patch.object(sync_payroll, 'retry', return_value=None) as mock_retry:
            # Call the task's bound function directly
            sync_payroll.push_request(payroll_run_id='456')
            # The task should have attempted to call the API and then retried
            mock_request.post.assert_called_once()
            mock_retry.assert_called_once_with(exc=mock_request.post.side_effect)

    def test_sync_payroll_missing_api_url(self, mock_request):
        """Edge case: ADP_API_URL environment variable is missing."""
        with patch.dict('os.environ', {}, clear=True):
            # When the env var is missing, the API call will use None as URL
            # This should raise an error; we verify it triggers a retry
            mock_request.post.side_effect = ValueError("Invalid URL None")
            with patch.object(sync_payroll, 'retry', return_value=None) as mock_retry:
                sync_payroll.push_request(payroll_run_id='789')
                mock_request.post.assert_called_once()
                mock_retry.assert_called_once()

    def test_sync_payroll_max_retries(self):
        """Verify the task is configured with max_retries=3 as intended."""
        assert sync_payroll.max_retries == 3

    def test_sync_payroll_is_bound(self):
        """Ensure the task is a bound Celery task (self is passed)."""
        assert sync_payroll.bind == True