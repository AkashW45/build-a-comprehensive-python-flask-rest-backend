import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, Response as FlaskResponse
import json

# Import the blueprint and proxy helpers from the source file
# Adjust the import path according to your project structure
from api_gateway.src.routes.proxy_routes import (
    proxy_bp,
    proxy_request,
    EMPLOYEE_SERVICE_URL,
    DEPARTMENT_SERVICE_URL,
    PAYROLL_SERVICE_URL,
    LEAVE_SERVICE_URL,
    PERFORMANCE_SERVICE_URL,
    RECRUITMENT_SERVICE_URL,
    INTEGRATION_SERVICE_URL,
    COMPLIANCE_SERVICE_URL,
)

@pytest.fixture
def client():
    """Create a Flask test app with the proxy blueprint and JWT configured."""
    app = Flask(__name__)
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret"
    })
    
    # Register the JWT extension without needing an init_app (simplified)
    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)
    
    # Register blueprint
    app.register_blueprint(proxy_bp)
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_token(client):
    """Generate a valid JWT access token."""
    from flask_jwt_extended import create_access_token
    with client.application.app_context():
        token = create_access_token(identity="test-user")
    return token

@pytest.fixture
def auth_headers(auth_token):
    """Return headers dict with a valid Authorization token."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def mock_requests():
    """Fixture that patches requests.request globally and returns a mock response."""
    with patch('api_gateway.src.routes.proxy_routes.requests') as mock_req:
        # Set up a default successful response
        mock_response = MagicMock()
        mock_response.content = b'{"message": "ok"}'
        mock_response.status_code = 200
        mock_response.headers.items.return_value = [('Content-Type', 'application/json')]
        mock_req.request.return_value = mock_response
        yield mock_req

class TestProxyRoutes:
    """Tests for the API gateway proxy routes."""

    def test_proxy_employees_get_happy_path(self, client, auth_headers, mock_requests):
        """GET /employees should forward correctly to the employee service."""
        response = client.get('/employees', headers=auth_headers)
        assert response.status_code == 200
        assert response.json == {"message": "ok"}
        mock_requests.request.assert_called_once_with(
            'get',
            f'{EMPLOYEE_SERVICE_URL}/employees/',
            headers=auth_headers,  # headers are forwarded (minus 'Host')
            data=b'',
            params={}
        )

    def test_proxy_employees_get_with_id_and_query_params(self, client, auth_headers, mock_requests):
        """GET /employees/123?active=true should forward path and query params."""
        response = client.get('/employees/123?active=true', headers=auth_headers)
        assert response.status_code == 200
        mock_requests.request.assert_called_once_with(
            'get',
            f'{EMPLOYEE_SERVICE_URL}/employees/123',
            headers=auth_headers,
            data=b'',
            params={'active': 'true'}
        )

    def test_proxy_employees_post_with_body(self, client, auth_headers, mock_requests):
        """POST /employees with JSON body should forward the data and method."""
        payload = {"name": "John Doe", "role": "dev"}
        response = client.post('/employees', json=payload, headers=auth_headers)
        assert response.status_code == 200
        mock_requests.request.assert_called_once()
        call_args = mock_requests.request.call_args[0]
        assert call_args[0] == 'post'
        assert call_args[1] == f'{EMPLOYEE_SERVICE_URL}/employees/'
        # The body is sent as raw data, so we check that it contains the payload
        assert json.loads(call_kwargs.get('data', b'')) == payload

    def test_proxy_departments_put_method(self, client, auth_headers, mock_requests):
        """PUT /departments/5 should forward PUT request."""
        response = client.put('/departments/5', headers=auth_headers, json={"name": "Updated"})
        assert response.status_code == 200
        mock_requests.request.assert_called_once_with(
            'put',
            f'{DEPARTMENT_SERVICE_URL}/departments/5',
            headers=auth_headers,
            data=json.dumps({"name": "Updated"}).encode(),
            params={}
        )

    def test_proxy_payroll_runs_get(self, client, auth_headers, mock_requests):
        """GET /payroll/runs should forward to payroll service."""
        response = client.get('/payroll/runs', headers=auth_headers)
        assert response.status_code == 200
        mock_requests.request.assert_called_once_with(
            'get',
            f'{PAYROLL_SERVICE_URL}/payroll/runs',
            headers=auth_headers,
            data=b'',
            params={}
        )

    def test_proxy_leaves_approve_path(self, client, auth_headers, mock_requests):
        """PUT /leaves/15/approve should forward as PUT."""
        response = client.put('/leaves/15/approve', headers=auth_headers)
        assert response.status_code == 200
        mock_requests.request.assert_called_once_with(
            'put',
            f'{LEAVE_SERVICE_URL}/leaves/15/approve',
            headers=auth_headers,
            data=b'',
            params={}
        )

    def test_proxy_recruitment_put_status(self, client, auth_headers, mock_requests):
        """PUT /recruitment/7/status should be forwarded."""
        response = client.put('/recruitment/7/status', headers=auth_headers, json={"status": "rejected"})
        assert response.status_code == 200
        mock_requests.request.assert_called_once_with(
            'put',
            f'{RECRUITMENT_SERVICE_URL}/recruitment/7/status',
            headers=auth_headers,
            data=json.dumps({"status": "rejected"}).encode(),
            params={}
        )

    def test_proxy_integrations_post(self, client, auth_headers, mock_requests):
        """POST /integrations/slack should forward."""
        response = client.post('/integrations/slack', headers=auth_headers, json={"message": "test"})
        assert response.status_code == 200
        mock_requests.request.assert_called_once_with(
            'post',
            f'{INTEGRATION_SERVICE_URL}/integrations/slack',
            headers=auth_headers,
            data=json.dumps({"message": "test"}).encode(),
            params={}
        )

    def test_proxy_compliance_delete(self, client, auth_headers, mock_requests):
        """DELETE /compliance/gdpr-export should be forwarded."""
        response = client.delete('/compliance/gdpr-export', headers=auth_headers)
        assert response.status_code == 200
        mock_requests.request.assert_called_once_with(
            'delete',
            f'{COMPLIANCE_SERVICE_URL}/compliance/gdpr-export',
            headers=auth_headers,
            data=b'',
            params={}
        )

    def test_proxy_returns_error_response_from_service(self, client, auth_headers, mock_requests):
        """When the downstream service returns an error, the proxy should reflect it."""
        error_response = MagicMock()
        error_response.content = b'{"error": "Not Found"}'
        error_response.status_code = 404
        error_response.headers.items.return_value = [('Content-Type', 'application/json')]
        mock_requests.request.return_value = error_response

        response = client.get('/employees/999', headers=auth_headers)
        assert response.status_code == 404
        assert response.json == {"error": "Not Found"}

    def test_proxy_service_unreachable_returns_500(self, client, auth_headers, mock_requests):
        """When the service is unreachable (ConnectionError), the proxy should raise 500."""
        mock_requests.request.side_effect = requests.exceptions.ConnectionError("No route to host")

        response = client.get('/employees', headers=auth_headers)
        # The Flask app will catch the exception and return 500
        assert response.status_code == 500

    def test_proxy_unauthenticated_returns_401(self, client):
        """Requests without JWT should be rejected with 401."""
        response = client.get('/employees')
        assert response.status_code == 401
        assert "Missing Authorization Header" in response.json.get("msg", "")

    def test_proxy_passes_custom_headers_from_request(self, client, auth_headers, mock_requests):
        """Non-Host headers like X-Correlation-ID should be forwarded."""
        custom_headers = {
            "Authorization": auth_headers["Authorization"],
            "X-Correlation-ID": "abc-123",
            "User-Agent": "pytest"
        }
        response = client.get('/employees', headers=custom_headers)
        assert response.status_code == 200
        # The mock should have been called with the merged headers (minus Host)
        called_headers = mock_requests.request.call_args[1]['headers']
        assert called_headers.get("X-Correlation-ID") == "abc-123"
        assert called_headers.get("Authorization") == auth_headers["Authorization"]

    def test_proxy_empty_path_generates_trailing_slash(self, client, auth_headers, mock_requests):
        """When path is empty, the proxied URL should include a trailing slash after the segment."""
        response = client.get('/employees', headers=auth_headers)
        assert mock_requests.request.call_args[0][1].endswith('/employees/')