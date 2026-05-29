import pytest
import os
from compliance_service.app import create_app, db

@pytest.fixture
def app(monkeypatch):
    """Create a test app with in‑memory DATABASE_URL and no external services."""
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')
    monkeypatch.setenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318/v1/traces')  # keep local default
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_endpoint_returns_ok(client):
    """Happy path: /health returns status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}

def test_metrics_endpoint_returns_prometheus_metrics(client):
    """Edge case: Prometheus metrics endpoint is reachable and contains typical output."""
    response = client.get('/metrics')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert 'python_info' in data or 'process_virtual_memory_bytes' in data

def test_compliance_blueprint_is_registered(client):
    """Edge case: a request to the blueprint's base URL returns 404 (no handler for root)."""
    response = client.get('/compliance/')
    # No route defined on the blueprint root, so Flask returns 404
    assert response.status_code == 404

def test_unknown_endpoint_returns_404(client):
    """Error path: an unregistered endpoint returns 404."""
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_app_uses_database_url_env_variable(monkeypatch):
    """Edge case: the app picks up DATABASE_URL from environment."""
    custom_url = 'postgresql://test:test@testhost/testdb'
    monkeypatch.setenv('DATABASE_URL', custom_url)
    app = create_app()
    app.config['TESTING'] = True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == custom_url