import json
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

from src.routes.compliance_routes import compliance_bp
from src.models.audit_log import AuditLog
from src.models.gdpr_request import GDPRRequest
from src.models.medical_leave import MedicalLeave


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(compliance_bp)
    with app.test_client() as client:
        yield client


# ------------------------------------------------------------------------------
# get_audit_logs
# ------------------------------------------------------------------------------

def test_get_audit_logs_returns_paginated_results(client):
    """Happy path: GET /audit-logs returns paginated logs with expected structure."""
    mock_log = MagicMock()
    mock_log.id = 1
    mock_log.user_id = 42
    mock_log.action = 'update'
    mock_log.resource_type = 'employee'
    mock_log.timestamp.isoformat.return_value = '2025-03-01T12:00:00'

    mock_paginate = MagicMock()
    mock_paginate.items = [mock_log]
    mock_paginate.total = 1
    mock_paginate.page = 1

    with patch('src.routes.compliance_routes.AuditLog.query') as mock_query:
        mock_query.order_by.return_value.paginate.return_value = mock_paginate
        response = client.get('/audit-logs?page=1&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert data['page'] == 1
        assert len(data['logs']) == 1
        assert data['logs'][0]['action'] == 'update'


def test_get_audit_logs_empty_no_content(client):
    """Edge case: no audit logs returns empty list with 200."""
    mock_paginate = MagicMock()
    mock_paginate.items = []
    mock_paginate.total = 0
    mock_paginate.page = 1

    with patch('src.routes.compliance_routes.AuditLog.query') as mock_query:
        mock_query.order_by.return_value.paginate.return_value = mock_paginate
        response = client.get('/audit-logs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 0
        assert data['logs'] == []


# ------------------------------------------------------------------------------
# request_gdpr_export
# ------------------------------------------------------------------------------

def test_request_gdpr_export_success(client):
    """Happy path: POST /gdpr/export with valid user_id returns 202 and creates request."""
    mock_gdpr = MagicMock(id=1)
    with patch('src.routes.compliance_routes.GDPRRequest', return_value=mock_gdpr), \
         patch('src.routes.compliance_routes.db.session') as mock_session:
        response = client.post('/gdpr/export', json={'user_id': 100})
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['message'] == 'Export requested'
        assert data['request_id'] == 1
        mock_session.add.assert_called_once_with(mock_gdpr)
        mock_session.commit.assert_called_once()


def test_request_gdpr_export_error_missing_user_id(client):
    """Error path: missing user_id raises KeyError -> 500 (no validation in source)."""
    response = client.post('/gdpr/export', json={})
    assert response.status_code == 500  # KeyError


# ------------------------------------------------------------------------------
# request_gdpr_forget
# ------------------------------------------------------------------------------

def test_request_gdpr_forget_success(client):
    """Happy path: POST /gdpr/forget with valid user_id returns 202 and creates request."""
    mock_gdpr = MagicMock(id=2)
    with patch('src.routes.compliance_routes.GDPRRequest', return_value=mock_gdpr), \
         patch('src.routes.compliance_routes.db.session') as mock_session:
        response = client.post('/gdpr/forget', json={'user_id': 200})
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['message'] == 'Forget requested'
        assert data['request_id'] == 2
        mock_session.add.assert_called_once_with(mock_gdpr)
        mock_session.commit.assert_called_once()


# ------------------------------------------------------------------------------
# handle_medical_leaves
# ------------------------------------------------------------------------------

def test_handle_medical_leaves_get(client):
    """Happy path: GET /medical-leaves returns all leaves."""
    mock_leave = MagicMock()
    mock_leave.id = 10
    mock_leave.employee_id = 5
    mock_leave.start_date.isoformat.return_value = '2025-04-01T08:00:00'

    with patch('src.routes.compliance_routes.MedicalLeave.query') as mock_query:
        mock_query.all.return_value = [mock_leave]
        response = client.get('/medical-leaves')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['id'] == 10
        assert data[0]['employee_id'] == 5


def test_handle_medical_leaves_post(client):
    """Happy path: POST /medical-leaves creates a new leave and returns 201."""
    mock_leave = MagicMock(id=99)
    with patch('src.routes.compliance_routes.MedicalLeave', return_value=mock_leave), \
         patch('src.routes.compliance_routes.db.session') as mock_session:
        payload = {'employee_id': 1, 'start_date': '2025-05-01', 'diagnosis': 'flu'}
        response = client.post('/medical-leaves', json=payload)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['id'] == 99
        mock_session.add.assert_called_once_with(mock_leave)
        mock_session.commit.assert_called_once()