import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from io import BytesIO

from src.routes.integration_routes import integration_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(integration_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_slack_notify_happy_path(client):
    with patch('src.routes.integration_routes.send_slack_notification.delay') as mock_delay:
        mock_task = MagicMock()
        mock_task.id = 'task-slack-123'
        mock_delay.return_value = mock_task

        response = client.post('/slack/notify', json={
            'message': 'Hello team',
            'channel': '#random'
        })

        assert response.status_code == 202
        assert response.json == {'task_id': 'task-slack-123'}
        mock_delay.assert_called_once_with('Hello team', '#random')

def test_slack_notify_error_missing_message(client):
    with patch('src.routes.integration_routes.send_slack_notification.delay') as mock_delay:
        # Missing required 'message' key should cause KeyError -> 500
        response = client.post('/slack/notify', json={
            'channel': '#random'
        })

        assert response.status_code == 500
        mock_delay.assert_not_called()

def test_email_send_happy_path(client):
    with patch('src.routes.integration_routes.send_email.delay') as mock_delay:
        mock_task = MagicMock()
        mock_task.id = 'task-email-456'
        mock_delay.return_value = mock_task

        response = client.post('/email/send', json={
            'to': 'user@example.com',
            'subject': 'Test',
            'body': 'This is a test'
        })

        assert response.status_code == 202
        assert response.json == {'task_id': 'task-email-456'}
        mock_delay.assert_called_once_with('user@example.com', 'Test', 'This is a test')

def test_s3_upload_happy_path(client):
    with patch('src.routes.integration_routes.upload_to_s3.delay') as mock_delay:
        mock_task = MagicMock()
        mock_task.id = 'task-s3-789'
        mock_delay.return_value = mock_task

        # Simulate a file upload
        data = {'file': (BytesIO(b'dummy content'), 'test.pdf')}
        response = client.post('/s3/upload', content_type='multipart/form-data', data=data)

        assert response.status_code == 202
        assert response.json == {'task_id': 'task-s3-789'}
        # The task was called with request.files (ImmutableMultiDict)
        assert mock_delay.called
        # Verify that the file was passed
        call_args = mock_delay.call_args[0][0]
        assert 'file' in call_args

def test_stripe_enroll_error_missing_user_id(client):
    with patch('src.routes.integration_routes.process_stripe_payment.delay') as mock_delay:
        # Missing required 'user_id'
        response = client.post('/stripe/enroll', json={
            'plan': 'premium'
        })

        assert response.status_code == 500
        mock_delay.assert_not_called()

def test_adp_sync_happy_path(client):
    with patch('src.routes.integration_routes.sync_payroll.delay') as mock_delay:
        mock_task = MagicMock()
        mock_task.id = 'task-adp-101'
        mock_delay.return_value = mock_task

        response = client.post('/adp/sync', json={
            'payroll_run_id': 42
        })

        assert response.status_code == 202
        assert response.json == {'task_id': 'task-adp-101'}
        mock_delay.assert_called_once_with(42)